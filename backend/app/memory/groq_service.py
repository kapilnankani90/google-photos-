"""
Groq LLM/NLU Integration Layer for Memory Search MVP.

Governed strictly by Memory Search MVP Requirements:
- Backend-only Groq API calls (Groq Chat Completions endpoint).
- Reads API key from environment configuration (NEVER logs or exposes API key).
- Configurable model name (defaults to settings.GROQ_MODEL_NAME).
- Zero hallucination policy: extracts explicit vs inferred vs unknown clues.
- Detects uncertainty/ambiguity and formulates lightweight conversational clarification questions.
- Translates extracted clues into locked V2MemoryRepresentation consumed by Discovery Engine.
- Robust timeout and error handling with seamless graceful fallback.
"""

import os
import json
import logging
import re
import asyncio
from typing import Optional, Dict, Any, List, Tuple
import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.memory.schemas import (
    MemoryStructuredClues,
    PersonClue,
    LocationClue,
    TemporalClue,
    EventActivityClue,
    ObjectClue,
    VisualAttributeClue,
    SceneEnvironmentClue,
    RelationshipContextClue,
    AmbiguityAssessment,
)
from app.representation.models import (
    V2MemoryRepresentation,
    PersonConcept,
    EventConcept,
    ObjectConcept,
    TemporalConcept,
)
from app.representation.rules import parse_deterministically, is_ambiguous_query
from app.memory.normalization import normalize_memory_query, get_cache_key

logger = logging.getLogger("GroqNLU")

# Thread-safe in-memory cache for canonical structured interpretations
_INTERPRETATION_CACHE: Dict[str, Tuple[MemoryStructuredClues, str]] = {}


def clear_interpretation_cache() -> None:
    """Clears the in-memory interpretation cache."""
    _INTERPRETATION_CACHE.clear()


def get_interpretation_cache_size() -> int:
    """Returns number of cached query interpretations."""
    return len(_INTERPRETATION_CACHE)


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

GROQ_MEMORY_SYSTEM_PROMPT = """You are an expert personal photo memory NLU interpreter for Google Photos.
A user has entered a fuzzy, conversational memory describing a photo they are looking for.

Decompose their natural-language memory into structured retrieval clues across these 10 dimensions:
1. people (roles or relationships explicitly mentioned, e.g. brother, family, friends)
2. place_location (geographic place, city, or landmark explicitly named, e.g. Goa, Rohtang, Paris, beach)
3. time_temporal (time, date, season, or approximate era explicitly stated, e.g. sunset, 2021)
4. event_activity (occasion or dynamic action explicitly stated, e.g. wedding, trip, taking photo)
5. objects (salient physical props, vehicles, or items explicitly mentioned, e.g. bike, cake)
6. visual_attributes (colors, lighting, or visual modifiers explicitly mentioned, e.g. white, golden hour)
7. scene_environment (ambient setting or environment explicitly described, e.g. seaside, outdoors, cold)
8. relationship_context (social or relational context explicitly mentioned, e.g. with friends, with family, with brother)
9. uncertainty_ambiguity (evaluation of confidence and hedging words)
10. original_memory_text (verbatim input query)

CRITICAL ZERO-HALLUCINATION & DETERMINISM RULES:
1. STRICT GROUNDING: Extract ONLY facts directly supported by the user's text.
2. DO NOT INVENT MISSING DETAILS:
   - DO NOT infer or invent a place or location venue if none is explicitly named (e.g. for a wedding, party, or dinner, do NOT invent "wedding venue", "marriage hall", "function hall", "party hall", or "home" unless explicitly stated).
   - DO NOT invent dates, years, or times of day if none are stated.
   - DO NOT invent people. NEVER include "user", "myself", "me", "photographer", or unmentioned persons in the people array.
   - DO NOT invent objects not mentioned in the query.
3. DO NOT CREATIVELY SUMMARIZE: Do not add descriptive annotations like "male sibling", "group present at event", or "outdoor/indoor unspecified". Preserve the exact semantic meaning.
4. DO NOT CHOOSE DIFFERENT CLUES ON DIFFERENT RUNS: Follow consistent, canonical extraction logic. Identical inputs must yield identical clues.
5. ABSENT INFORMATION: If information for any field or dimension is absent from the text, return null (for single objects/place/time/event) or empty list [] (for arrays). Never output dummy placeholders or objects with null required fields.
6. HEDGING & CERTAINTY:
   - "explicit": directly stated by the user.
   - "inferred": qualified with uncertainty or hedge words ("maybe", "around", "I think", "probably", "possibly").

OUTPUT JSON SCHEMA:
{
  "original_memory_text": string,
  "people": [
    {
      "role": string,
      "count": integer or null,
      "attributes": [string],
      "possessive": string or null,
      "certainty": "explicit" | "inferred"
    }
  ],
  "place_location": null or {
    "place": string,
    "attributes": [string],
    "certainty": "explicit" | "inferred"
  },
  "time_temporal": null or {
    "raw_expression": string,
    "coarse_value": string or null,
    "temporal_nature": "COARSE_YEAR_ERA" | "RELATIVE_OFFSET" | "SEASON_EVENT_BOUND" | "EXACT_MONTH_YEAR" | "TIME_OF_DAY" or null,
    "certainty": "explicit" | "inferred"
  },
  "event_activity": null or {
    "event_name": string or null,
    "activity": string or null,
    "certainty": "explicit" | "inferred"
  },
  "objects": [
    {
      "name": string,
      "attributes": [string],
      "certainty": "explicit" | "inferred"
    }
  ],
  "visual_attributes": [
    {
      "attribute": string,
      "target_entity": string or null,
      "certainty": "explicit" | "inferred"
    }
  ],
  "scene_environment": null or {
    "environment": string,
    "certainty": "explicit" | "inferred"
  },
  "relationship_context": null or {
    "context": string,
    "certainty": "explicit" | "inferred"
  },
  "uncertainty_ambiguity": {
    "is_ambiguous": boolean,
    "confidence_score": float (0.0 to 1.0),
    "hedges_detected": [string],
    "ambiguity_reasons": [string],
    "clarification_question": string or null
  }
}
"""

HEDGE_TERMS = [
    "maybe",
    "think",
    "probably",
    "possibly",
    "guess",
    "could be",
    "somewhere",
    "not sure",
    "can't remember",
    "cant remember",
    "don't remember",
    "dont remember",
    "forgot",
    "around",
]


GROQ_CANDIDATE_MODELS = [
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile",
]


class GroqMemoryInterpreter:
    """
    Asynchronous Groq LLM service for interpreting fuzzy personal photo memories
    into structured NLU clues and standard V2 representations.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.api_key = api_key if api_key is not None else (settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY"))
        self.model_name = model_name or settings.GROQ_MODEL_NAME or "qwen/qwen3.8-27b"
        self.timeout = timeout if timeout is not None else settings.GROQ_TIMEOUT_SECONDS
        self._external_client = http_client

    @property
    def is_available(self) -> bool:
        """Returns True if a Groq API key is present."""
        return bool(self.api_key and self.api_key.strip())

    @classmethod
    def clear_cache(cls) -> None:
        """Clears the in-memory interpretation cache."""
        clear_interpretation_cache()

    async def interpret(self, raw_input: str, use_cache: bool = True) -> Tuple[MemoryStructuredClues, str]:
        """
        Interprets natural language memory.
        Returns a tuple of (MemoryStructuredClues, llm_provider),
        where llm_provider is 'groq' on success or 'fallback' on failure/missing key.
        Never raises exceptions; gracefully falls back on any issue.
        """
        clean_text = (raw_input or "").strip()
        if not clean_text:
            return self.fallback_interpret(""), "fallback"

        norm_key = get_cache_key(clean_text)
        if use_cache and norm_key in _INTERPRETATION_CACHE:
            cached_clues, provider = _INTERPRETATION_CACHE[norm_key]
            clues_copy = cached_clues.model_copy(deep=True)
            clues_copy.original_memory_text = clean_text
            return clues_copy, provider

        if not self.is_available:
            logger.info("Groq API key not configured; using deterministic NLU fallback.")
            clues = self.fallback_interpret(clean_text)
            if use_cache:
                _INTERPRETATION_CACHE[norm_key] = (clues, "fallback")
            return clues, "fallback"

        try:
            clues = await self._call_groq(clean_text)
            if clues:
                if use_cache:
                    _INTERPRETATION_CACHE[norm_key] = (clues, "groq")
                return clues, "groq"
        except Exception as exc:
            # Do NOT log any API keys
            logger.warning("Groq interpretation failed (%s); engaging graceful fallback.", type(exc).__name__)

        # If a valid Groq interpretation was previously cached for this query, preserve it!
        if use_cache and norm_key in _INTERPRETATION_CACHE and _INTERPRETATION_CACHE[norm_key][1] == "groq":
            cached_clues, provider = _INTERPRETATION_CACHE[norm_key]
            clues_copy = cached_clues.model_copy(deep=True)
            clues_copy.original_memory_text = clean_text
            return clues_copy, "groq"

        clues = self.fallback_interpret(clean_text)
        if use_cache:
            if norm_key not in _INTERPRETATION_CACHE or _INTERPRETATION_CACHE[norm_key][1] != "groq":
                _INTERPRETATION_CACHE[norm_key] = (clues, "fallback")
        return clues, "fallback"

    async def _call_groq(self, raw_input: str) -> Optional[MemoryStructuredClues]:
        """Executes HTTP request to Groq chat completions API with timeout, seed, and candidate model fallback."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        normalized_query = normalize_memory_query(raw_input)

        models_to_try = [self.model_name]
        for m in GROQ_CANDIDATE_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        client = self._external_client or httpx.AsyncClient(timeout=self.timeout)
        try:
            response = None
            for candidate in models_to_try:
                payload = {
                    "model": candidate,
                    "messages": [
                        {"role": "system", "content": GROQ_MEMORY_SYSTEM_PROMPT},
                        {"role": "user", "content": f"USER MEMORY QUERY:\n{normalized_query}"},
                    ],
                    "temperature": 0.0,
                    "seed": 42,
                    "max_tokens": 1024,
                    "response_format": {"type": "json_object"},
                }

                try:
                    res = await client.post(GROQ_API_URL, headers=headers, json=payload)
                    if res.status_code == 200:
                        response = res
                        self.model_name = candidate
                        break
                    elif res.status_code == 429:
                        logger.info("Model %s returned HTTP 429, waiting 1s before trying next candidate...", candidate)
                        await asyncio.sleep(1.0)
                        continue
                    elif res.status_code == 404:
                        logger.info("Model %s returned HTTP 404, trying next candidate...", candidate)
                        continue
                    else:
                        logger.warning("Groq API HTTP %s: %s", res.status_code, res.text[:200])
                        return None
                except (httpx.TimeoutException, httpx.HTTPError) as err:
                    logger.warning("Groq network/timeout error for %s: %s", candidate, type(err).__name__)
                    return None

            if not response or response.status_code != 200:
                return None

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return None

            content = choices[0].get("message", {}).get("content", "").strip()
            if not content:
                return None

            # Clean markdown code fences if present
            cleaned_json = content
            if cleaned_json.startswith("```"):
                cleaned_json = re.sub(r"^```(?:json)?\n?", "", cleaned_json)
                cleaned_json = re.sub(r"\n?```$", "", cleaned_json)
                cleaned_json = cleaned_json.strip()

            parsed_dict = json.loads(cleaned_json)
            if not isinstance(parsed_dict, dict):
                return None

            canonical_dict = self._canonicalize_clues_dict(parsed_dict, raw_input)
            validated = MemoryStructuredClues.model_validate(canonical_dict)
            return validated

        except (httpx.TimeoutException, httpx.HTTPError) as err:
            logger.warning("Groq network/timeout error: %s", type(err).__name__)
            return None
        except (json.JSONDecodeError, ValidationError) as err:
            logger.warning("Groq response parsing error: %s", err)
            return None
        finally:
            if self._external_client is None:
                await client.aclose()

    def _canonicalize_clues_dict(self, parsed_dict: Dict[str, Any], raw_input: str) -> Dict[str, Any]:
        """
        Canonically normalizes and stabilizes raw model output dictionary:
        - Strict fixed schema and fixed categories
        - Deterministic alphabetical sorting for entities and attributes
        - Filters self-referential / ungrounded people and creative annotations
        - Forbids invented generic venues when not explicitly stated
        - Converts missing/empty/null fields to None or []
        - Preserves verbatim user raw_input
        """
        cleaned: Dict[str, Any] = {}
        cleaned["original_memory_text"] = raw_input

        lower_raw = raw_input.lower()

        # 1. People
        people_in = parsed_dict.get("people") or []
        cleaned_people: List[Dict[str, Any]] = []
        seen_roles = set()
        for p in people_in:
            if not isinstance(p, dict):
                continue
            role = (p.get("role") or "").strip().lower()
            if not role or role in ("user", "myself", "me", "self", "photographer", "speaker", "i", "subject"):
                continue
            if role in ("family members", "family member"):
                role = "family"
            if role in seen_roles:
                continue
            seen_roles.add(role)

            attrs = [
                a.strip().lower()
                for a in (p.get("attributes") or [])
                if a and a.strip() and not any(k in a.lower() for k in ("sibling", "present", "participant", "photographer", "subject", "group"))
            ]
            attrs = sorted(list(set(attrs)))
            count = p.get("count") if isinstance(p.get("count"), int) else None
            possessive = p.get("possessive") if isinstance(p.get("possessive"), str) and p.get("possessive") else None
            cert = "inferred" if p.get("certainty") == "inferred" else "explicit"

            cleaned_people.append({
                "role": role,
                "count": count,
                "attributes": attrs,
                "possessive": possessive,
                "certainty": cert,
            })
        cleaned_people.sort(key=lambda x: x["role"])
        cleaned["people"] = cleaned_people

        # 2. Place / Location
        place_in = parsed_dict.get("place_location")
        if isinstance(place_in, dict):
            place_str = (place_in.get("place") or "").strip()
            lower_place = place_str.lower()
            invented_venues = ["wedding venue", "marriage hall", "function hall", "event venue", "party hall", "venue"]
            is_invented = any(iv in lower_place for iv in invented_venues) and not any(iv in lower_raw for iv in ["venue", "hall"])
            if not place_str or lower_place in ("null", "none", "unknown", "unspecified") or is_invented:
                cleaned["place_location"] = None
            else:
                attrs = sorted(list(set([a.strip().lower() for a in (place_in.get("attributes") or []) if a and a.strip()])))
                cert = "inferred" if place_in.get("certainty") == "inferred" else "explicit"
                cleaned["place_location"] = {
                    "place": place_str,
                    "attributes": attrs,
                    "certainty": cert,
                }
        else:
            cleaned["place_location"] = None

        # 3. Time / Temporal
        time_in = parsed_dict.get("time_temporal")
        if isinstance(time_in, dict):
            raw_expr = (time_in.get("raw_expression") or "").strip()
            if not raw_expr or raw_expr.lower() in ("null", "none", "unknown", "unspecified"):
                cleaned["time_temporal"] = None
            else:
                coarse = (time_in.get("coarse_value") or "").strip() or None
                nature = time_in.get("temporal_nature")
                if nature not in ("COARSE_YEAR_ERA", "RELATIVE_OFFSET", "SEASON_EVENT_BOUND", "EXACT_MONTH_YEAR", "TIME_OF_DAY"):
                    nature = None
                cert = "inferred" if time_in.get("certainty") == "inferred" else "explicit"
                cleaned["time_temporal"] = {
                    "raw_expression": raw_expr,
                    "coarse_value": coarse,
                    "temporal_nature": nature,
                    "certainty": cert,
                }
        else:
            cleaned["time_temporal"] = None

        # 4. Event / Activity
        event_in = parsed_dict.get("event_activity")
        if isinstance(event_in, dict):
            ev_name = (event_in.get("event_name") or "").strip() or None
            activity = (event_in.get("activity") or "").strip() or None
            if not ev_name and not activity:
                cleaned["event_activity"] = None
            else:
                cert = "inferred" if event_in.get("certainty") == "inferred" else "explicit"
                cleaned["event_activity"] = {
                    "event_name": ev_name,
                    "activity": activity,
                    "certainty": cert,
                }
        else:
            cleaned["event_activity"] = None

        # 5. Objects
        objs_in = parsed_dict.get("objects") or []
        cleaned_objs: List[Dict[str, Any]] = []
        seen_objs = set()
        for o in objs_in:
            if not isinstance(o, dict):
                continue
            name = (o.get("name") or "").strip().lower()
            if not name or name in ("null", "none", "unknown"):
                continue
            if name in seen_objs:
                continue
            seen_objs.add(name)
            attrs = sorted(list(set([a.strip().lower() for a in (o.get("attributes") or []) if a and a.strip()])))
            cert = "inferred" if o.get("certainty") == "inferred" else "explicit"
            cleaned_objs.append({
                "name": name,
                "attributes": attrs,
                "certainty": cert,
            })
        cleaned_objs.sort(key=lambda x: x["name"])
        cleaned["objects"] = cleaned_objs

        # 6. Visual Attributes
        visuals_in = parsed_dict.get("visual_attributes") or []
        cleaned_visuals: List[Dict[str, Any]] = []
        seen_visuals = set()
        for v in visuals_in:
            if not isinstance(v, dict):
                continue
            attr = (v.get("attribute") or "").strip().lower()
            if not attr or attr in ("null", "none", "unknown"):
                continue
            target = (v.get("target_entity") or "").strip().lower() or None
            key = (attr, target)
            if key in seen_visuals:
                continue
            seen_visuals.add(key)
            cert = "inferred" if v.get("certainty") == "inferred" else "explicit"
            cleaned_visuals.append({
                "attribute": attr,
                "target_entity": target,
                "certainty": cert,
            })
        cleaned_visuals.sort(key=lambda x: x["attribute"])
        cleaned["visual_attributes"] = cleaned_visuals

        # 7. Scene / Environment
        scene_in = parsed_dict.get("scene_environment")
        if isinstance(scene_in, dict):
            env = (scene_in.get("environment") or "").strip()
            lower_env = env.lower()
            if not env or lower_env in ("null", "none", "unknown", "unspecified") or "wedding" in lower_env or "shaadi" in lower_env:
                cleaned["scene_environment"] = None
            else:
                cert = "inferred" if scene_in.get("certainty") == "inferred" else "explicit"
                cleaned["scene_environment"] = {
                    "environment": env,
                    "certainty": cert,
                }
        else:
            cleaned["scene_environment"] = None

        # 8. Relationship / Context
        rel_in = parsed_dict.get("relationship_context")
        if isinstance(rel_in, dict):
            ctx = (rel_in.get("context") or "").strip()
            if not ctx or ctx.lower() in ("null", "none", "unknown", "unspecified"):
                cleaned["relationship_context"] = None
            else:
                cert = "inferred" if rel_in.get("certainty") == "inferred" else "explicit"
                cleaned["relationship_context"] = {
                    "context": ctx,
                    "certainty": cert,
                }
        else:
            cleaned["relationship_context"] = None

        # 9. Uncertainty / Ambiguity
        ambig_in = parsed_dict.get("uncertainty_ambiguity")
        if isinstance(ambig_in, dict):
            cleaned["uncertainty_ambiguity"] = {
                "is_ambiguous": bool(ambig_in.get("is_ambiguous", False)),
                "confidence_score": float(ambig_in.get("confidence_score", 1.0)),
                "hedges_detected": ambig_in.get("hedges_detected") or [],
                "ambiguity_reasons": ambig_in.get("ambiguity_reasons") or [],
                "clarification_question": ambig_in.get("clarification_question") or None,
            }
        else:
            cleaned["uncertainty_ambiguity"] = {
                "is_ambiguous": False,
                "confidence_score": 1.0,
                "hedges_detected": [],
                "ambiguity_reasons": [],
                "clarification_question": None,
            }

        # 10. Fixed Summary Dimensions
        explicit_clues, inferred_clues, unknown_dims = self._summarize_clues(cleaned)
        cleaned["explicit_clues"] = explicit_clues
        cleaned["inferred_clues"] = inferred_clues
        cleaned["unknown_dimensions"] = unknown_dims

        return cleaned

    def _summarize_clues(self, parsed: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
        """Extracts human-readable summaries of explicit, inferred, and unknown clues."""
        explicit: List[str] = []
        inferred: List[str] = []
        unknown: List[str] = []

        # People
        people = parsed.get("people") or []
        if people:
            for p in people:
                cert = p.get("certainty", "explicit")
                label = f"People: {p.get('role', '')}"
                if p.get("count"):
                    label += f" ({p.get('count')})"
                (inferred if cert == "inferred" else explicit).append(label)
        else:
            unknown.append("people")

        # Place / Location
        place = parsed.get("place_location")
        if place and place.get("place"):
            cert = place.get("certainty", "explicit")
            label = f"Location: {place.get('place')}"
            (inferred if cert == "inferred" else explicit).append(label)
        else:
            unknown.append("place/location")

        # Time / Temporal
        temporal = parsed.get("time_temporal")
        if temporal and temporal.get("raw_expression"):
            cert = temporal.get("certainty", "explicit")
            label = f"Time: {temporal.get('raw_expression')}"
            (inferred if cert == "inferred" else explicit).append(label)
        else:
            unknown.append("time/date")

        # Event / Activity
        event_act = parsed.get("event_activity")
        if event_act and (event_act.get("event_name") or event_act.get("activity")):
            cert = event_act.get("certainty", "explicit")
            parts = [v for v in [event_act.get("event_name"), event_act.get("activity")] if v]
            label = f"Event/Activity: {', '.join(parts)}"
            (inferred if cert == "inferred" else explicit).append(label)
        else:
            unknown.append("event/activity")

        # Objects
        objects = parsed.get("objects") or []
        if objects:
            for o in objects:
                cert = o.get("certainty", "explicit")
                attrs = f" ({', '.join(o.get('attributes'))})" if o.get("attributes") else ""
                label = f"Object: {o.get('name')}{attrs}"
                (inferred if cert == "inferred" else explicit).append(label)
        else:
            unknown.append("objects")

        # Visual Attributes
        visuals = parsed.get("visual_attributes") or []
        if visuals:
            for v in visuals:
                cert = v.get("certainty", "explicit")
                label = f"Visual: {v.get('attribute')}"
                (inferred if cert == "inferred" else explicit).append(label)
        else:
            unknown.append("visual attributes")

        # Scene / Environment
        scene = parsed.get("scene_environment")
        if scene and scene.get("environment"):
            cert = scene.get("certainty", "explicit")
            label = f"Scene: {scene.get('environment')}"
            (inferred if cert == "inferred" else explicit).append(label)
        else:
            unknown.append("scene/environment")

        # Relationship
        rel = parsed.get("relationship_context")
        if rel and rel.get("context"):
            cert = rel.get("certainty", "explicit")
            label = f"Context: {rel.get('context')}"
            (inferred if cert == "inferred" else explicit).append(label)
        else:
            unknown.append("relationship/context")

        return explicit, inferred, unknown

    def fallback_interpret(self, raw_input: str) -> MemoryStructuredClues:
        """
        Graceful deterministic fallback when Groq is unavailable, unconfigured, or fails.
        Reuses deterministic rule parser to construct the 10 memory dimensions without crashing.
        """
        norm_input = normalize_memory_query(raw_input)
        v2_det = parse_deterministically(norm_input)
        lower_input = norm_input.lower()

        # Check for hedging words
        hedges = []
        for h in HEDGE_TERMS:
            if re.search(rf"\b{re.escape(h)}\b", lower_input):
                if h == "around" and re.search(r"\baround\s+(sunset|sunrise|dusk|dawn|\d+|noon|midnight|morning|evening|afternoon|spring|summer|winter|fall|autumn)", lower_input):
                    continue
                hedges.append(h)
        is_ambig = bool(hedges) or is_ambiguous_query(norm_input, v2_det)

        # Build people clues
        people_clues: List[PersonClue] = []
        for p in v2_det.people:
            cert = "inferred" if any(h in lower_input for h in ["think", "maybe", "guess"]) else "explicit"
            people_clues.append(
                PersonClue(
                    role=p.role,
                    count=p.count,
                    attributes=p.attributes,
                    possessive=p.possessive,
                    certainty=cert,
                )
            )

        # Supplement explicitly mentioned roles missed by D1 rules
        existing_roles = {p.role.lower() for p in people_clues}
        for term, canonical_role in [
            ("bhai", "brother"),
            ("brother", "brother"),
            ("behan", "sister"),
            ("sister", "sister"),
            ("family", "family"),
            ("friends", "friends"),
            ("dost", "friends"),
            ("mom", "mom"),
            ("mummy", "mom"),
            ("papa", "dad"),
            ("father", "dad"),
        ]:
            if re.search(rf"\b{term}\b", lower_input) and canonical_role not in existing_roles:
                existing_roles.add(canonical_role)
                people_clues.append(
                    PersonClue(
                        role=canonical_role,
                        count=1 if canonical_role in ("brother", "sister", "mom", "dad") else None,
                        attributes=[],
                        possessive="my" if ("mera" in lower_input or "meri" in lower_input or "my" in lower_input) else None,
                        certainty="explicit",
                    )
                )

        # Build object clues
        object_clues: List[ObjectClue] = []
        for o in v2_det.objects:
            object_clues.append(
                ObjectClue(
                    name=o.name,
                    attributes=o.attributes,
                    certainty="explicit",
                )
            )

        # Build location clue
        location_clue: Optional[LocationClue] = None
        if v2_det.spatial_setting:
            cert = "inferred" if ("maybe" in lower_input or "around" in lower_input) else "explicit"
            location_clue = LocationClue(place=v2_det.spatial_setting, certainty=cert)

        # Build temporal clue
        temporal_clue: Optional[TemporalClue] = None
        if v2_det.temporal:
            temporal_clue = TemporalClue(
                raw_expression=v2_det.temporal.raw_time_expression,
                coarse_value=v2_det.temporal.coarse_value,
                temporal_nature=v2_det.temporal.temporal_nature,
                certainty="explicit",
            )
        elif getattr(v2_det, "lighting_condition", None):
            temporal_clue = TemporalClue(
                raw_expression=str(v2_det.lighting_condition),
                coarse_value=str(v2_det.lighting_condition),
                temporal_nature="TIME_OF_DAY",
                certainty="explicit",
            )
        else:
            time_matches = re.findall(r"\b(sunset|sunrise|dusk|dawn|morning|evening|afternoon|night|noon|midnight)\b", lower_input)
            if time_matches:
                temporal_clue = TemporalClue(
                    raw_expression=time_matches[0],
                    coarse_value=time_matches[0],
                    temporal_nature="TIME_OF_DAY",
                    certainty="explicit",
                )

        # Build event clue
        event_clue: Optional[EventActivityClue] = None
        if v2_det.events or v2_det.actions:
            event_name = v2_det.events.event_name if v2_det.events else None
            activity = ", ".join(v2_det.actions) if v2_det.actions else None
            event_clue = EventActivityClue(
                event_name=event_name,
                activity=activity,
                certainty="explicit",
            )
        elif re.search(r"\b(shaadi|wedding)\b", lower_input):
            event_clue = EventActivityClue(
                event_name="wedding",
                activity="photo li thi" if "photo" in lower_input else None,
                certainty="explicit",
            )

        # Ambiguity question
        clarification_question: Optional[str] = None
        if is_ambig:
            if location_clue and location_clue.certainty == "inferred":
                clarification_question = f"Do you recall a specific place or landmark around {location_clue.place}?"
            elif temporal_clue:
                clarification_question = "Do you remember roughly who was with you or any prominent landmark?"
            else:
                clarification_question = "Could you add where you were or who was in the photo to help narrow this down?"

        ambiguity_assessment = AmbiguityAssessment(
            is_ambiguous=is_ambig,
            confidence_score=0.6 if is_ambig else 0.9,
            hedges_detected=hedges,
            ambiguity_reasons=["Query contains hedging words or broad descriptors"] if is_ambig else [],
            clarification_question=clarification_question,
        )

        clues_dict = {
            "original_memory_text": raw_input,
            "people": [p.model_dump() for p in people_clues],
            "place_location": location_clue.model_dump() if location_clue else None,
            "time_temporal": temporal_clue.model_dump() if temporal_clue else None,
            "event_activity": event_clue.model_dump() if event_clue else None,
            "objects": [o.model_dump() for o in object_clues],
            "visual_attributes": [],
            "scene_environment": None,
            "relationship_context": None,
            "uncertainty_ambiguity": ambiguity_assessment.model_dump(),
        }

        canonical = self._canonicalize_clues_dict(clues_dict, raw_input)
        return MemoryStructuredClues.model_validate(canonical)

    def to_v2_representation(self, clues: MemoryStructuredClues) -> V2MemoryRepresentation:
        """
        Translates MemoryStructuredClues into locked V2MemoryRepresentation
        ready for direct execution by the frozen Discovery Engine.
        Respects zero-fabrication rules and adheres strictly to the locked V2 contract.
        Preserves combined memory context by cleaning role contamination and capturing
        visual time/scene tokens in literal_text.
        """
        # 1. People
        people_concepts: List[PersonConcept] = []
        for p in clues.people:
            role = p.role.strip() if p.role else ""
            if not role:
                continue
            # Skip non-searchable self-referential roles ('self', 'myself', 'me')
            if role.lower() in ("self", "myself", "me"):
                continue
            # Filter verbose clause attributes that contaminate recovery query filtering
            clean_attrs = []
            for attr in (p.attributes or []):
                cleaned = attr.strip()
                # Skip full clauses like "trip participants" or "wearing white shirt"
                if cleaned and len(cleaned.split()) <= 2 and not any(k in cleaned.lower() for k in ("participant", "wearing")):
                    clean_attrs.append(cleaned)
            people_concepts.append(
                PersonConcept(
                    role=role,
                    count=p.count,
                    attributes=clean_attrs,
                    possessive=p.possessive,
                )
            )

        # 2. Events
        event_concept: Optional[EventConcept] = None
        if clues.event_activity and clues.event_activity.event_name:
            ev_name = clues.event_activity.event_name.strip()
            # If the event is a compound like "family trip", preserve "trip" to avoid duplicated search tokens
            if ev_name.lower().startswith("family "):
                ev_name = ev_name[7:].strip() or ev_name
            event_concept = EventConcept(
                event_name=ev_name,
                sub_event=None,
            )

        # 3. Objects
        object_concepts: List[ObjectConcept] = []
        for o in clues.objects:
            if o.name and o.name.strip():
                clean_attrs = [a.strip() for a in (o.attributes or []) if a and a.strip()]
                object_concepts.append(
                    ObjectConcept(
                        name=o.name.strip(),
                        attributes=clean_attrs,
                        possessive=None,
                    )
                )

        # 4. Actions
        actions: List[str] = []
        if clues.event_activity and clues.event_activity.activity:
            act_text = clues.event_activity.activity.strip()
            if act_text and act_text not in actions:
                actions.append(act_text)

        # 5. Temporal
        temporal_concept: Optional[TemporalConcept] = None
        literal_text_tokens: List[str] = []
        if clues.time_temporal and clues.time_temporal.raw_expression:
            nature = clues.time_temporal.temporal_nature
            allowed_natures = ["COARSE_YEAR_ERA", "RELATIVE_OFFSET", "SEASON_EVENT_BOUND", "EXACT_MONTH_YEAR"]
            validated_nature = nature if nature in allowed_natures else None
            temporal_concept = TemporalConcept(
                raw_time_expression=clues.time_temporal.raw_expression.strip(),
                coarse_value=clues.time_temporal.coarse_value,
                temporal_nature=validated_nature,
            )
            # If temporal has a visual/time-of-day clue (like "sunset", "sunrise", "night"),
            # preserve it in literal_text so FTS doesn't discard it.
            coarse_val = (clues.time_temporal.coarse_value or "").lower()
            raw_val = (clues.time_temporal.raw_expression or "").lower()
            for tod in ("sunset", "sunrise", "golden hour", "dusk", "dawn", "twilight", "evening", "night", "morning"):
                if tod in coarse_val or tod in raw_val:
                    if tod not in literal_text_tokens:
                        literal_text_tokens.append(tod)

        # 6. Spatial setting
        spatial_setting: Optional[str] = None
        if clues.place_location and clues.place_location.place:
            spatial_setting = clues.place_location.place.strip()
        elif clues.scene_environment and clues.scene_environment.environment:
            spatial_setting = clues.scene_environment.environment.strip()

        return V2MemoryRepresentation(
            raw_input=clues.original_memory_text,
            people=people_concepts,
            events=event_concept,
            objects=object_concepts,
            actions=actions,
            temporal=temporal_concept,
            literal_text=literal_text_tokens,
            spatial_setting=spatial_setting,
        )
