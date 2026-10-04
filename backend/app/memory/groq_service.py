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

logger = logging.getLogger("GroqNLU")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

GROQ_MEMORY_SYSTEM_PROMPT = """You are an expert personal photo memory NLU interpreter for Google Photos.
A user has entered a fuzzy, conversational memory describing a photo they are looking for.

Your task is to decompose their natural-language memory into structured retrieval clues across these 10 dimensions:
1. people (roles, counts, modifiers, e.g. friends, sisters, mom)
2. place/location (geographic destination, city, beach, e.g. Goa, Rohtang, Paris)
3. time/date or approximate time (coarse era, year, time of day, e.g. sunset, 4 years ago, 2021)
4. event/activity (occasion or physical activity, e.g. trip, standing near sea, wedding)
5. objects (salient props, natural elements, e.g. sea, bike, cake, snow)
6. visual attributes (colors, lighting, e.g. golden hour, yellow dress)
7. scene/environment (ambient setting, e.g. seaside, outdoors, cold)
8. relationship/context (social context, e.g. with friends, family trip)
9. uncertainty/ambiguity (evaluation of confidence and hedging)
10. original_memory_text (verbatim input query)

CRITICAL GROUNDING & HONESTY RULES:
1. DO NOT INVENT OR FABRICATE FACTS. Do not assume dates, names, or places not mentioned or strongly implied.
2. Distinguish clue certainty:
   - "explicit": directly stated by the user (e.g., "standing near the sea", "sunset")
   - "inferred": qualified with uncertainty or hedge words like "maybe", "around", "I think", "probably", "possibly" (e.g. "maybe around Goa", "think friends were with me")
   - "unknown": completely absent in the memory
3. Ambiguity & Clarification:
   If the memory has high ambiguity, vague locations ("maybe around Goa"), or uncertainty markers:
   - Set is_ambiguous = true
   - List the hedge words detected (e.g., ["maybe", "think", "around"])
   - Provide a natural, lightweight clarification question to ask the user (e.g. "Were you in North Goa (like Baga or Anjuna) or South Goa, or do you remember approximately which year this was?").
   If the memory is crisp and clear without hedging, set is_ambiguous = false and clarification_question = null.

OUTPUT SCHEMA (Must be valid JSON only):
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
  "place_location": {
    "place": string,
    "attributes": [string],
    "certainty": "explicit" | "inferred"
  } or null,
  "time_temporal": {
    "raw_expression": string,
    "coarse_value": string or null,
    "temporal_nature": "COARSE_YEAR_ERA" | "RELATIVE_OFFSET" | "SEASON_EVENT_BOUND" | "EXACT_MONTH_YEAR" | "TIME_OF_DAY" or null,
    "certainty": "explicit" | "inferred"
  } or null,
  "event_activity": {
    "event_name": string or null,
    "activity": string or null,
    "certainty": "explicit" | "inferred"
  } or null,
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
  "scene_environment": {
    "environment": string,
    "certainty": "explicit" | "inferred"
  } or null,
  "relationship_context": {
    "context": string,
    "certainty": "explicit" | "inferred"
  } or null,
  "uncertainty_ambiguity": {
    "is_ambiguous": boolean,
    "confidence_score": float (0.0 to 1.0),
    "hedges_detected": [string],
    "ambiguity_reasons": [string],
    "clarification_question": string or null
  }
}
"""

HEDGE_TERMS = ["maybe", "think", "around", "probably", "possibly", "guess", "could be", "somewhere", "not sure"]


GROQ_CANDIDATE_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
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

    async def interpret(self, raw_input: str) -> Tuple[MemoryStructuredClues, str]:
        """
        Interprets natural language memory.
        Returns a tuple of (MemoryStructuredClues, llm_provider),
        where llm_provider is 'groq' on success or 'fallback' on failure/missing key.
        Never raises exceptions; gracefully falls back on any issue.
        """
        clean_text = (raw_input or "").strip()
        if not clean_text:
            return self.fallback_interpret(""), "fallback"

        if not self.is_available:
            logger.info("Groq API key not configured; using deterministic NLU fallback.")
            return self.fallback_interpret(clean_text), "fallback"

        try:
            clues = await self._call_groq(clean_text)
            if clues:
                return clues, "groq"
        except Exception as exc:
            # Do NOT log any API keys
            logger.warning("Groq interpretation failed (%s); engaging graceful fallback.", type(exc).__name__)

        return self.fallback_interpret(clean_text), "fallback"

    async def _call_groq(self, raw_input: str) -> Optional[MemoryStructuredClues]:
        """Executes HTTP request to Groq chat completions API with timeout and candidate model fallback."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

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
                        {"role": "user", "content": f"USER MEMORY QUERY:\n{raw_input}"},
                    ],
                    "temperature": 0.0,
                    "max_tokens": 1024,
                    "response_format": {"type": "json_object"},
                }

                try:
                    res = await client.post(GROQ_API_URL, headers=headers, json=payload)
                    if res.status_code == 200:
                        response = res
                        self.model_name = candidate
                        break
                    elif res.status_code in (404, 429):
                        logger.info("Model %s returned HTTP %s, trying next candidate...", candidate, res.status_code)
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

            # Ensure original text provenance
            parsed_dict["original_memory_text"] = raw_input

            # Compute summary lists if not present
            explicit_clues, inferred_clues, unknown_dims = self._summarize_clues(parsed_dict)
            parsed_dict["explicit_clues"] = explicit_clues
            parsed_dict["inferred_clues"] = inferred_clues
            parsed_dict["unknown_dimensions"] = unknown_dims

            validated = MemoryStructuredClues.model_validate(parsed_dict)
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
        v2_det = parse_deterministically(raw_input)
        lower_input = raw_input.lower()

        # Check for hedging words
        hedges = [h for h in HEDGE_TERMS if re.search(rf"\b{h}\b", lower_input)]
        is_ambig = bool(hedges) or is_ambiguous_query(raw_input, v2_det)

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

        explicit, inferred, unknown = self._summarize_clues(clues_dict)
        clues_dict["explicit_clues"] = explicit
        clues_dict["inferred_clues"] = inferred
        clues_dict["unknown_dimensions"] = unknown

        return MemoryStructuredClues.model_validate(clues_dict)

    def to_v2_representation(self, clues: MemoryStructuredClues) -> V2MemoryRepresentation:
        """
        Translates MemoryStructuredClues into locked V2MemoryRepresentation
        ready for direct execution by the frozen Discovery Engine.
        Respects zero-fabrication rules and adheres strictly to the locked V2 contract.
        """
        # 1. People
        people_concepts: List[PersonConcept] = []
        for p in clues.people:
            if p.role and p.role.strip():
                people_concepts.append(
                    PersonConcept(
                        role=p.role.strip(),
                        count=p.count,
                        attributes=p.attributes or [],
                        possessive=p.possessive,
                    )
                )

        # 2. Events
        event_concept: Optional[EventConcept] = None
        if clues.event_activity and clues.event_activity.event_name:
            event_concept = EventConcept(
                event_name=clues.event_activity.event_name.strip(),
                sub_event=None,
            )

        # 3. Objects
        object_concepts: List[ObjectConcept] = []
        for o in clues.objects:
            if o.name and o.name.strip():
                object_concepts.append(
                    ObjectConcept(
                        name=o.name.strip(),
                        attributes=o.attributes or [],
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
        if clues.time_temporal and clues.time_temporal.raw_expression:
            nature = clues.time_temporal.temporal_nature
            allowed_natures = ["COARSE_YEAR_ERA", "RELATIVE_OFFSET", "SEASON_EVENT_BOUND", "EXACT_MONTH_YEAR"]
            validated_nature = nature if nature in allowed_natures else None
            temporal_concept = TemporalConcept(
                raw_time_expression=clues.time_temporal.raw_expression.strip(),
                coarse_value=clues.time_temporal.coarse_value,
                temporal_nature=validated_nature,
            )

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
            literal_text=[],
            spatial_setting=spatial_setting,
        )
