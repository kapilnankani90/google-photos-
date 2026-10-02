"""
Structured Gemini Fallback Parser for Ambiguous Open-Domain Queries.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 7.2, 14.3, 23, 24)
- part1_memory_representation_schema_v2.md

Requirements:
- Invoked ONLY for ambiguous open-domain queries where deterministic extraction is insufficient
- Uses environment variable GEMINI_API_KEY (never logged, printed, or committed)
- System remains fully testable without real Gemini credentials (mockable boundary)
- Output is strictly constrained to the V2MemoryRepresentation schema
- Robust error handling: catches API timeouts, rate limits, network failures, and malformed JSON
- Returns None on any failure, ensuring deterministic fallback without fabricated fields
"""

import os
import json
import logging
import re
from typing import Optional, Dict, Any
import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.representation.models import V2MemoryRepresentation

logger = logging.getLogger("GeminiParser")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

V2_PROMPT_SYSTEM = """You are the Google Photos V2 Memory Representation Interpreter.
Your sole job is to translate the user's natural-language memory query into the locked V2 JSON structure.

STRICT EXTRACTION RULES:
1. Preserve verbatim wording in raw_input.
2. DO NOT invent or fabricate details not explicitly stated (no specific dates, no unmentioned names, no imaginary locations).
3. If an entity is not recalled, leave the corresponding field empty or null.
4. Output MUST BE strictly valid JSON matching the schema below with NO additional keys.

ALLOWED SCHEMA:
{
  "raw_input": string (verbatim input),
  "people": [
    {
      "role": string,
      "count": integer or null,
      "attributes": [string],
      "possessive": string or null
    }
  ],
  "events": {
    "event_name": string,
    "sub_event": string or null
  } or null,
  "objects": [
    {
      "name": string,
      "attributes": [string],
      "possessive": string or null
    }
  ],
  "actions": [string],
  "temporal": {
    "raw_time_expression": string,
    "coarse_value": string or null,
    "temporal_nature": "COARSE_YEAR_ERA" | "RELATIVE_OFFSET" | "SEASON_EVENT_BOUND" | "EXACT_MONTH_YEAR" or null
  } or null,
  "literal_text": [string],
  "spatial_setting": string or null
}
"""


class GeminiParserClient:
    """
    Client for structured fallback intent interpretation via Gemini 2.5 Flash.
    Designed for testability with clean dependency injection.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: float = 5.0,
        http_client: Optional[httpx.Client] = None,
    ):
        self.api_key = api_key if api_key is not None else (settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY"))
        self.timeout = timeout
        self._external_client = http_client

    @property
    def is_available(self) -> bool:
        """Returns True if a Gemini API key is configured."""
        return bool(self.api_key and self.api_key.strip())

    def parse_open_domain(self, raw_input: str) -> Optional[V2MemoryRepresentation]:
        """
        Parses an ambiguous open-domain query into a validated V2MemoryRepresentation.
        Returns None if Gemini is unavailable, times out, or returns invalid/malformed data.
        """
        if not self.is_available:
            logger.info("Gemini API key not configured; skipping LLM fallback.")
            return None

        prompt = f"{V2_PROMPT_SYSTEM}\n\nUSER MEMORY INPUT:\n{raw_input}"

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.8,
                "maxOutputTokens": 1024,
                "responseMimeType": "application/json",
            },
        }

        try:
            client = self._external_client or httpx.Client(timeout=self.timeout)
            try:
                # Mask key in any debug logs
                logger.debug("Dispatching structured interpretation request to Gemini API...")
                response = client.post(
                    f"{GEMINI_API_URL}?key={self.api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
            finally:
                if self._external_client is None:
                    client.close()

            if response.status_code != 200:
                logger.warning(
                    f"Gemini API returned non-200 status code: {response.status_code}"
                )
                return None

            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                logger.warning("Gemini response contained zero candidates.")
                return None

            content_parts = candidates[0].get("content", {}).get("parts", [])
            if not content_parts:
                logger.warning("Gemini candidate contained no content parts.")
                return None

            raw_text = content_parts[0].get("text", "").strip()
            if not raw_text:
                logger.warning("Gemini returned empty text response.")
                return None

            # Clean markdown code fences if present
            cleaned_json = raw_text
            if cleaned_json.startswith("```"):
                cleaned_json = re.sub(r"^```(?:json)?\n?", "", cleaned_json)
                cleaned_json = re.sub(r"\n?```$", "", cleaned_json)
                cleaned_json = cleaned_json.strip()

            parsed_dict = json.loads(cleaned_json)
            if not isinstance(parsed_dict, dict):
                logger.warning("Gemini returned JSON that is not a dictionary.")
                return None

            # Guarantee query provenance: force verbatim raw_input
            parsed_dict["raw_input"] = raw_input

            # Strictly validate against locked Pydantic V2 schema (extra="forbid")
            validated = V2MemoryRepresentation.model_validate(parsed_dict)
            return validated

        except httpx.TimeoutException:
            logger.warning("Gemini API call timed out after %s seconds.", self.timeout)
            return None
        except httpx.HTTPError as err:
            logger.warning("HTTP error during Gemini API call: %s", type(err).__name__)
            return None
        except json.JSONDecodeError as err:
            logger.warning("Malformed JSON in Gemini response: %s", err)
            return None
        except ValidationError as err:
            logger.warning("Gemini output violated V2 schema contract: %s", err)
            return None
        except Exception as err:
            logger.error("Unexpected error in Gemini fallback parser: %s", type(err).__name__)
            return None
