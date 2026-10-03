"""
Retrieval & Scoring Pipeline Package.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 8, 10–13, 24)
- part1_discovery_engine_architecture_final.md (Stages 3–6)

Exports PostgreSQL Lexical FTS retrieval classes, signal generators, and data models.
"""

from app.retrieval.models import (
    RetrievalFilter,
    ScoreBreakdown,
    CandidateResult,
    CoverageEvaluation,
    DiscoveryResponse,
)
from app.retrieval.signals import (
    RetrievalSignals,
    generate_retrieval_signals,
)
from app.retrieval.retriever import MultiPathRetriever
from app.retrieval.pipeline import DiscoveryEnginePipeline

__all__ = [
    "RetrievalFilter",
    "ScoreBreakdown",
    "CandidateResult",
    "CoverageEvaluation",
    "DiscoveryResponse",
    "RetrievalSignals",
    "generate_retrieval_signals",
    "MultiPathRetriever",
    "DiscoveryEnginePipeline",
]
