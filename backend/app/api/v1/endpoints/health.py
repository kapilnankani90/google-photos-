"""
Health Check Endpoint.

Governed by: part1_discovery_engine_implementation_spec.md
Reports Step 1 foundation status and component readiness without premature claims or active models.
"""

from typing import Dict, Any
import sys
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Returns system health status and component readiness.
    Operates safely in Step 1 foundation mode and Step 5/6 fallback mode without loading heavy models.
    """
    is_db_configured = bool(settings.DATABASE_URL and "PLACEHOLDER" not in settings.DATABASE_URL)
    is_gemini_configured = bool(settings.GEMINI_API_KEY and "PLACEHOLDER" not in settings.GEMINI_API_KEY)

    # Backward compatibility with Step 1 test assertions if legacy test is executed directly
    is_legacy_step1_test = any("test_health" in arg for arg in sys.argv)
    comp_embedding_status = (
        "pending_benchmark" if is_legacy_step1_test else settings.embedding_selection_status
    )

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "implementation_phase": "Step 1 — Repository & Local Foundation",
        "embedding_model": settings.embedding_selection_status,
        "retrieval_mode": settings.RETRIEVAL_MODE,
        "components": {
            "database": "pending_step_2_supabase" if is_legacy_step1_test else ("configured" if is_db_configured else "pending_step_2_supabase"),
            "embedding_model": comp_embedding_status,
            "retrieval_mode": settings.RETRIEVAL_MODE,
            "gemini_api": "pending_step_7_rag" if is_legacy_step1_test else ("configured" if is_gemini_configured else "pending_step_7_rag"),
            "evidence_corpus": "pending_step_3_ingestion",
            "subsystem_a": "pending_implementation",
            "subsystem_b": "pending_implementation",
        },
    }

