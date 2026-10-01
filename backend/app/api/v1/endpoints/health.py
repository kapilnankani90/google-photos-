"""
Health Check Endpoint.

Governed by: part1_discovery_engine_implementation_spec.md
Reports Step 1 foundation status and component readiness without premature claims or active models.
"""

from typing import Dict, Any
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Returns system health status and component readiness.
    Operates safely in Step 1 foundation mode without active secrets or premature model selection.
    """
    is_db_configured = bool(settings.DATABASE_URL and "PLACEHOLDER" not in settings.DATABASE_URL)
    is_gemini_configured = bool(settings.GEMINI_API_KEY and "PLACEHOLDER" not in settings.GEMINI_API_KEY)

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "implementation_phase": "Step 1 — Repository & Local Foundation",
        "components": {
            "database": "configured" if is_db_configured else "pending_step_2_supabase",
            "embedding_model": settings.embedding_selection_status,  # "pending_benchmark"
            "gemini_api": "configured" if is_gemini_configured else "pending_step_7_rag",
            "evidence_corpus": "pending_step_3_ingestion",
            "subsystem_a": "pending_implementation",
            "subsystem_b": "pending_implementation",
        },
    }
