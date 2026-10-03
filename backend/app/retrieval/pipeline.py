"""
Discovery Engine Pipeline Orchestrator.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 7, 8, 10–13, 24, 28)
- part1_discovery_engine_architecture_final.md (Stages 2–6)

Connects the validated Discovery Engine stages into a single callable pipeline:
Raw Input
    ↓
Stage 2: Memory Interpretation (MemoryInterpreter -> V2MemoryRepresentation)
    ↓
Stage 3: Retrieval Signal Generation (generate_retrieval_signals -> RetrievalSignals)
    ↓
Stage 4: Candidate Discovery & Coverage Checking (MultiPathRetriever -> tsvector FTS)
    ↓
Stage 5: Compositional Multi-Clue Matching (MultiPathRetriever -> Bound Attribute Bonus)
    ↓
Stage 6: Contextual Result Organization (MultiPathRetriever -> Ranked DiscoveryResponse)
"""

import logging
from typing import Optional, Union
import asyncpg

from app.core.config import settings
from app.representation.interpreter import MemoryInterpreter
from app.representation.models import V2MemoryRepresentation
from app.retrieval.models import RetrievalFilter, DiscoveryResponse
from app.retrieval.retriever import MultiPathRetriever

logger = logging.getLogger("DiscoveryEnginePipeline")


class DiscoveryEnginePipeline:
    """
    Unified Discovery Engine Pipeline executing Stages 2 through 6.
    Operates in active RETRIEVAL_MODE="lexical_fts" without loading neural embedding models.
    """

    def __init__(
        self,
        interpreter: Optional[MemoryInterpreter] = None,
        retriever: Optional[MultiPathRetriever] = None,
    ):
        self.interpreter = interpreter or MemoryInterpreter()
        self.retriever = retriever or MultiPathRetriever()

    async def run(
        self,
        query: Union[str, V2MemoryRepresentation],
        filters: Optional[RetrievalFilter] = None,
        top_k: int = 10,
        conn: Optional[asyncpg.Connection] = None,
        db_url: Optional[str] = None,
        allow_gemini_fallback: bool = True,
    ) -> DiscoveryResponse:
        """
        Executes the end-to-end Discovery Engine retrieval pipeline:

        1. Stage 2: Memory Interpretation
           If input is a raw string, parses into V2MemoryRepresentation.
           If input is already a V2MemoryRepresentation, preserves it directly.

        2. Stages 3-6: Multi-Path Retrieval & Compositional Ranking
           Delegates to MultiPathRetriever.retrieve():
           - Stage 3: Generates structured retrieval signals (visual entities, bound attributes, temporal).
           - Stage 4: Queries PostgreSQL Lexical FTS using GIN index idx_chunks_fts; applies structured
             and temporal filters; checks coverage; executes single-pass broadening recovery if needed.
           - Stage 5: Evaluates bound entity-attribute relationships and awards +1.5 bonus.
           - Stage 6: Organizes candidates chronologically and by composite score.

        Returns:
           DiscoveryResponse conforming strictly to Section 18.2 schema.
        """
        logger.info("Executing Discovery Engine pipeline in %s mode", settings.RETRIEVAL_MODE)

        # ---------------------------------------------------------------------
        # Stage 2: Memory Interpretation
        # ---------------------------------------------------------------------
        if isinstance(query, str):
            raw_input_text = query
            v2_representation = self.interpreter.interpret(
                raw_input=raw_input_text,
                allow_gemini_fallback=allow_gemini_fallback,
            )
        elif isinstance(query, V2MemoryRepresentation):
            v2_representation = query
        else:
            raise TypeError(
                f"Query must be str or V2MemoryRepresentation, got {type(query).__name__}"
            )

        # ---------------------------------------------------------------------
        # Stages 3–6: Signal Generation, Candidate Retrieval, Scoring & Organization
        # ---------------------------------------------------------------------
        response = await self.retriever.retrieve(
            representation=v2_representation,
            filters=filters,
            top_k=top_k,
            conn=conn,
            db_url=db_url,
        )

        return response
