"""
MemoryInterpreter Pipeline Orchestrator.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 7.1, 7.2, 8.2, 23)
- part1_memory_representation_schema_v2.md

Pipeline Flow:
Natural-language memory/query
        ↓
sanitization & vernacular particle isolation
        ↓
deterministic interpretation
        ↓
ambiguity / open-domain check
        ↓
Gemini structured fallback (if ambiguous & configured)
        ↓
Pydantic schema validation
        ↓
validated V2 Memory Frame
"""

import logging
from typing import Optional

from app.representation.models import V2MemoryRepresentation
from app.representation.rules import (
    sanitize_input,
    parse_deterministically,
    is_ambiguous_query,
)
from app.representation.gemini_parser import GeminiParserClient

logger = logging.getLogger("MemoryInterpreter")


class MemoryInterpreter:
    """
    Translates raw natural-language photo memory queries into validated V2 Memory Frames.
    Executes deterministic parsing first, with controlled fallback to structured Gemini
    for ambiguous open-domain queries.
    """

    def __init__(self, gemini_client: Optional[GeminiParserClient] = None):
        self.gemini_client = gemini_client or GeminiParserClient()

    def interpret(
        self,
        raw_input: str,
        allow_gemini_fallback: bool = True,
        force_gemini: bool = False,
    ) -> V2MemoryRepresentation:
        """
        Executes memory interpretation on the input query:
        1. Preserves raw_input verbatim.
        2. Executes deterministic parsing first.
        3. If forced or if query is ambiguous and deterministic parsing is insufficient,
           attempts Gemini structured fallback.
        4. Validates and returns the final V2MemoryRepresentation.
        """
        if not raw_input or not raw_input.strip():
            # Return empty valid frame with verbatim empty input
            return V2MemoryRepresentation(raw_input=raw_input or "")

        # 1. Deterministic Layer
        deterministic_frame = parse_deterministically(raw_input)

        if not allow_gemini_fallback and not force_gemini:
            return deterministic_frame

        # 2. Check if query is ambiguous or fallback is explicitly forced
        needs_fallback = force_gemini or is_ambiguous_query(raw_input, deterministic_frame)

        if needs_fallback and self.gemini_client.is_available:
            logger.info("Query classified as ambiguous/open-domain; invoking structured Gemini fallback...")
            gemini_result = self.gemini_client.parse_open_domain(raw_input)
            if gemini_result is not None:
                logger.info("Successfully interpreted query via structured Gemini fallback.")
                return gemini_result
            else:
                logger.warning(
                    "Gemini fallback yielded no valid frame; falling back safely to deterministic baseline."
                )

        return deterministic_frame
