"""
API v1 Router Definition.

Governed by: part1_discovery_engine_implementation_spec.md (Section 18)
Mounts existing foundation endpoints and establishes clean mount points for subsequent phases.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, discover, transcribe, memory_search

api_v1_router = APIRouter(prefix="/api/v1")

# Mount health check endpoint
api_v1_router.include_router(health.router, tags=["Health"])

# Mount discovery engine endpoint (Phase 3 Integration)
api_v1_router.include_router(discover.router, prefix="/discover", tags=["Discovery Engine"])

# Mount audio transcription endpoint (Voice Input)
api_v1_router.include_router(transcribe.router, prefix="/transcribe", tags=["Voice Transcription"])

# Mount AI-Native Memory Search endpoint (Groq NLU Layer)
api_v1_router.include_router(memory_search.router, prefix="/memory", tags=["Memory Search"])

# Future Phase Router Mount Points (Documented for seamless Phase 4-5 addition):
# api_v1_router.include_router(research.router, prefix="/research", tags=["Research Insights"])
# api_v1_router.include_router(evidence.router, prefix="/evidence", tags=["Evidence Repository"])
# api_v1_router.include_router(experiment.router, prefix="/experiment", tags=["Benchmark Regression"])
