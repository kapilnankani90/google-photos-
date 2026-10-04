"""
Memory Search MVP API Endpoints.

Integrates Groq LLM NLU layer with the existing frozen Discovery Engine.
Provides:
- POST /api/v1/memory/search: Conversational NLU interpretation + Discovery Engine retrieval
- POST /api/v1/memory/interpret: Lightweight NLU interpretation & clarification generation
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.memory.schemas import (
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryInterpretationResponse,
)
from app.memory.groq_service import GroqMemoryInterpreter
from app.retrieval.pipeline import DiscoveryEnginePipeline

logger = logging.getLogger("MemorySearchEndpoint")

router = APIRouter()


def get_groq_interpreter() -> GroqMemoryInterpreter:
    """Dependency provider for GroqMemoryInterpreter."""
    return GroqMemoryInterpreter()


def get_discovery_pipeline() -> DiscoveryEnginePipeline:
    """Dependency provider for the existing DiscoveryEnginePipeline."""
    return DiscoveryEnginePipeline()


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
    pipeline: DiscoveryEnginePipeline = Depends(get_discovery_pipeline),
) -> MemorySearchResponse:
    """
    Primary endpoint for Memory Search MVP.
    1. Interprets natural language memory via Groq into structured clues.
    2. Maps clues cleanly into frozen V2MemoryRepresentation.
    3. Executes Discovery Engine retrieval pipeline.
    4. Returns candidate results alongside transparent clue provenance and clarification questions.
    """
    clean_input = request.raw_input.strip()
    if not clean_input:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A non-empty natural language memory query is required.",
        )

    import time
    start_time = time.perf_counter()

    try:
        # Step 1: Interpret via Groq NLU (with automatic graceful fallback)
        structured_clues, provider = await interpreter.interpret(clean_input)

        # Step 2: Convert to locked V2 representation
        v2_frame = interpreter.to_v2_representation(structured_clues)

        # Step 3: Execute Discovery Engine retrieval using the V2 frame
        discovery_res = await pipeline.run(
            query=v2_frame,
            top_k=request.top_k,
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return MemorySearchResponse(
            original_memory_text=clean_input,
            raw_input=clean_input,
            llm_provider=provider,  # type: ignore[arg-type]
            model_name=interpreter.model_name if provider == "groq" else None,
            structured_clues=structured_clues,
            clarification_question=structured_clues.uncertainty_ambiguity.clarification_question,
            is_ambiguous=structured_clues.uncertainty_ambiguity.is_ambiguous,
            v2_frame=discovery_res.v2_frame,
            retrieval_signals=discovery_res.retrieval_signals,
            results=discovery_res.results,
            coverage_status=discovery_res.coverage_status,
            controlled_recovery_triggered=discovery_res.controlled_recovery_triggered,
            candidate_pool_size=discovery_res.candidate_pool_size,
            execution_time_ms=elapsed_ms,
        )
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

    structured_clues, provider = await interpreter.interpret(clean_input)
    v2_frame = interpreter.to_v2_representation(structured_clues)

    return MemoryInterpretationResponse(
        original_memory_text=clean_input,
        llm_provider=provider,  # type: ignore[arg-type]
        model_name=interpreter.model_name if provider == "groq" else None,
        structured_clues=structured_clues,
        v2_representation=v2_frame,
        is_ambiguous=structured_clues.uncertainty_ambiguity.is_ambiguous,
        clarification_question=structured_clues.uncertainty_ambiguity.clarification_question,
    )
