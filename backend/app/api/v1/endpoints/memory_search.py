"""
Memory Search MVP API Endpoints.

Integrates Groq LLM NLU layer with the existing frozen Discovery Engine.
Provides:
- POST /api/v1/memory/search: Conversational NLU interpretation + Discovery Engine retrieval
- POST /api/v1/memory/interpret: Lightweight NLU interpretation & clarification generation
"""

import logging
import time
import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.memory.schemas import (
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryInterpretationResponse,
)
from app.memory.groq_service import GroqMemoryInterpreter
from app.memory.response_cache import (
    get_cached_search_response,
    cache_search_response,
    get_cached_interpretation_response,
    cache_interpretation_response,
    make_deterministic_candidate_ordering,
)
from app.retrieval.models import CandidateResult, DiscoveryResponse

logger = logging.getLogger("MemorySearchEndpoint")

router = APIRouter()


def get_groq_interpreter() -> GroqMemoryInterpreter:
    """Dependency provider for GroqMemoryInterpreter."""
    return GroqMemoryInterpreter()


def is_eligible_consumer_memory(candidate: CandidateResult) -> bool:
    """
    D2 Presentation-layer eligibility gate:
    Includes only genuine successful memory/photo-retrieval episodes.
    Excludes product complaints, feature requests, and failure diagnostics.
    """
    meta = getattr(candidate, "metadata", None) or {}
    if not isinstance(meta, dict):
        meta = getattr(meta, "model_dump", lambda: {})() if hasattr(meta, "model_dump") else getattr(meta, "__dict__", {})

    evidence_type = str(meta.get("evidence_type") or "").upper()
    if evidence_type in ("FAILURE", "PAIN_POINT"):
        return False

    tags = meta.get("category_tags") or []
    if isinstance(tags, (list, tuple, set)):
        upper_tags = {str(t).upper() for t in tags}
        if "SEARCH_PROBLEM" in upper_tags:
            return False
    elif isinstance(tags, str) and tags.upper() == "SEARCH_PROBLEM":
        return False

    failure_mode = meta.get("failure_mode")
    if failure_mode and str(failure_mode).upper() not in ("NONE", "NULL", ""):
        return False

    methodology = str(meta.get("methodology") or "").upper()
    if methodology == "UNSOLICITED_PUBLIC":
        return False

    if evidence_type == "SUCCESS" or methodology == "PROMPTED_INTERVIEW":
        return True

    source = str(meta.get("source") or meta.get("source_type") or "").upper()
    if source in ("PHOTO_ARCHIVE", "USER_INTERVIEW"):
        return True

    if not evidence_type and not methodology and not failure_mode:
        return True

GENERIC_META_STOPWORDS = {
    "photo", "photos", "picture", "pictures", "image", "images", "remember",
    "memory", "memories", "took", "taken", "taking", "look", "looking",
    "search", "show", "find", "nice", "good", "there", "were", "with",
    "from", "about", "that", "this", "some", "our", "my", "me", "i", "we",
    "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "was"
}

DOCUMENT_TAGS = {"DOCUMENT_SEARCH", "OCR", "RECEIPT_SEARCH"}
DOCUMENT_TERMS = {"document", "receipt", "paper", "text", "bill", "invoice", "license", "card"}


def is_grounded_consumer_memory(
    candidate: CandidateResult,
    v2_frame: Optional[Any] = None,
    structured_clues: Optional[Any] = None,
    raw_query: str = "",
) -> bool:
    """
    Consumer grounding boundary:
    Ensures candidates returned by broad lexical retrieval are genuinely grounded
    in the consumer's memory clues, rather than accidental lexical matches on
    generic meta-words like 'photo' or document-scanning research cases.
    """
    meta = getattr(candidate, "metadata", None) or {}
    if not isinstance(meta, dict):
        meta = getattr(meta, "model_dump", lambda: {})() if hasattr(meta, "model_dump") else getattr(meta, "__dict__", {})

    tags = meta.get("category_tags") or []
    upper_tags = {str(t).upper() for t in tags} if isinstance(tags, (list, tuple, set)) else {str(tags).upper()}

    # 1. Reject document-search candidates unless query explicitly requested a document
    query_lower = raw_query.lower()
    is_doc_query = any(doc_word in query_lower for doc_word in DOCUMENT_TERMS)
    if not is_doc_query and upper_tags.intersection(DOCUMENT_TAGS):
        return False

    # 2. If candidate has compositional bound entity bonus (+1.5), it is strongly grounded
    score_breakdown = getattr(candidate, "score_breakdown", None)
    if score_breakdown and getattr(score_breakdown, "bound_bonus", 0.0) > 0.0:
        return True

    # 3. Collect salient clue tokens from structured dimensions (people, events, objects, places, etc.)
    salient_clues: set[str] = set()
    if structured_clues:
        for p in getattr(structured_clues, "people", []) or []:
            if getattr(p, "role", None):
                salient_clues.update(p.role.lower().split())
        for o in getattr(structured_clues, "objects", []) or []:
            if getattr(o, "name", None):
                salient_clues.update(o.name.lower().split())
            for attr in getattr(o, "attributes", []) or []:
                salient_clues.update(attr.lower().split())
        ev = getattr(structured_clues, "event_activity", None)
        if ev:
            if getattr(ev, "event_name", None):
                salient_clues.update(ev.event_name.lower().split())
            if getattr(ev, "activity", None):
                salient_clues.update(ev.activity.lower().split())
        pl = getattr(structured_clues, "place_location", None)
        if pl and getattr(pl, "place", None):
            salient_clues.update(pl.place.lower().split())
        for vd in getattr(structured_clues, "visual_details", []) or []:
            salient_clues.update(vd.lower().split())

    if v2_frame:
        for p in getattr(v2_frame, "people", []) or []:
            if getattr(p, "role", None):
                salient_clues.update(p.role.lower().split())
        for o in getattr(v2_frame, "objects", []) or []:
            if getattr(o, "name", None):
                salient_clues.update(o.name.lower().split())
        if getattr(v2_frame, "spatial_setting", None):
            salient_clues.update(v2_frame.spatial_setting.lower().split())
        ev = getattr(v2_frame, "events", None)
        if ev and getattr(ev, "event_name", None):
            salient_clues.update(ev.event_name.lower().split())

    # Filter out generic stopwords
    salient_tokens = {w for w in salient_clues if len(w) > 2 and w not in GENERIC_META_STOPWORDS}

    # If salient clues were identified, the candidate content or tags must match at least one
    if salient_tokens:
        candidate_text = (getattr(candidate, "content", "") + " " + " ".join(upper_tags)).lower()
        if not any(token in candidate_text for token in salient_tokens):
            return False

    return True


@router.post(
    "/search",
    response_model=MemorySearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Conversational Memory Search with Groq NLU",
    description=(
        "Interprets a fuzzy personal memory via Groq LLM into 10 structured dimensions, "
        "separating explicit vs inferred clues and identifying ambiguity. "
        "Passes the resulting validated V2 frame to the Discovery Engine for candidate retrieval."
    ),
)
async def search_memory(
    request: MemorySearchRequest,
    interpreter: GroqMemoryInterpreter = Depends(get_groq_interpreter),
) -> MemorySearchResponse:
    """
    Primary endpoint for Memory Search MVP.
    1. Interprets natural language memory via Groq into structured clues.
    2. Maps clues cleanly into frozen V2MemoryRepresentation.
    3. Executes Discovery Engine retrieval via HTTP POST to D1 /api/v1/discover.
    4. Returns candidate results alongside transparent clue provenance and clarification questions.
    """
    clean_input = request.raw_input.strip()
    if not clean_input:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A non-empty natural language memory query is required.",
        )

    # Check D2 Full Search Response Cache (canonical normalized key lookup)
    cached_search = get_cached_search_response(
        clean_input,
        top_k=request.top_k,
        enable_recovery=request.enable_recovery,
    )
    if cached_search is not None:
        return cached_search

    start_time = time.perf_counter()

    try:
        # Step 1: Interpret via Groq NLU (with automatic graceful fallback)
        structured_clues, provider = await interpreter.interpret(clean_input)

        # Step 2: Convert to locked V2 representation
        v2_frame = interpreter.to_v2_representation(structured_clues)

        # Step 3: Execute Discovery Engine retrieval via HTTP POST to D1
        d1_url = f"{settings.DISCOVERY_ENGINE_URL.rstrip('/')}/api/v1/discover"
        payload = {
            "v2_representation": v2_frame.model_dump(),
            "top_k": request.top_k,
            "enable_recovery": request.enable_recovery,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.GROQ_TIMEOUT_SECONDS) as client:
                res = await client.post(d1_url, json=payload)
                if res.status_code != 200:
                    logger.error("Failed to call D1 Discovery Engine: HTTP %s - %s", res.status_code, res.text[:200])
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Memory search failed: D1 Discovery Engine returned an error",
                    )
                discovery_res = DiscoveryResponse.model_validate(res.json())
        except httpx.HTTPError as http_err:
            logger.error("Failed to call D1 Discovery Engine: %s", type(http_err).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Memory search failed: Unable to connect to D1 Discovery Engine",
            )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Step 4: D2 consumer-facing candidate eligibility & grounding filter
        consumer_results = [
            cand
            for cand in discovery_res.results
            if is_eligible_consumer_memory(cand)
            and is_grounded_consumer_memory(cand, v2_frame, structured_clues, clean_input)
        ]

        # Recompute deterministic candidate ordering and sequential ranks (1..N)
        ordered_results = make_deterministic_candidate_ordering(consumer_results)

        full_response = MemorySearchResponse(
            original_memory_text=clean_input,
            raw_input=clean_input,
            llm_provider=provider,  # type: ignore[arg-type]
            model_name=interpreter.model_name if provider == "groq" else None,
            structured_clues=structured_clues,
            clarification_question=structured_clues.uncertainty_ambiguity.clarification_question,
            is_ambiguous=structured_clues.uncertainty_ambiguity.is_ambiguous,
            v2_frame=discovery_res.v2_frame,
            retrieval_signals=discovery_res.retrieval_signals,
            results=ordered_results,
            coverage_status=discovery_res.coverage_status,
            controlled_recovery_triggered=discovery_res.controlled_recovery_triggered,
            candidate_pool_size=len(ordered_results),
            execution_time_ms=elapsed_ms,
        )

        # Step 5: Cache COMPLETE response under canonical normalized query key
        cache_search_response(
            clean_input,
            full_response,
            top_k=request.top_k,
            enable_recovery=request.enable_recovery,
        )

        return full_response

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Memory search execution error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memory search failed: {str(exc)}",
        )


@router.post(
    "/interpret",
    response_model=MemoryInterpretationResponse,
    status_code=status.HTTP_200_OK,
    summary="Interpret Fuzzy Memory Query into Structured Clues",
    description="Translates a natural language query into 10-dimension structured clues without executing database retrieval.",
)
async def interpret_memory(
    request: MemorySearchRequest,
    interpreter: GroqMemoryInterpreter = Depends(get_groq_interpreter),
) -> MemoryInterpretationResponse:
    """Interpretation-only endpoint for debugging, transparent clue previews, or multi-turn dialogues."""
    clean_input = request.raw_input.strip()
    if not clean_input:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A non-empty natural language memory query is required.",
        )

    # Check cached interpretation
    cached_interp = get_cached_interpretation_response(clean_input)
    if cached_interp is not None:
        return cached_interp

    structured_clues, provider = await interpreter.interpret(clean_input)
    v2_frame = interpreter.to_v2_representation(structured_clues)

    interp_response = MemoryInterpretationResponse(
        original_memory_text=clean_input,
        llm_provider=provider,  # type: ignore[arg-type]
        model_name=interpreter.model_name if provider == "groq" else None,
        structured_clues=structured_clues,
        v2_representation=v2_frame,
        is_ambiguous=structured_clues.uncertainty_ambiguity.is_ambiguous,
        clarification_question=structured_clues.uncertainty_ambiguity.clarification_question,
    )

    cache_interpretation_response(clean_input, interp_response)
    return interp_response
