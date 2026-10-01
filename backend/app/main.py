"""
FastAPI Application Entry Point.

Governed by: part1_discovery_engine_implementation_spec.md
Provides the backend REST API foundation for the Discovery Engine and Evidence Console.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown logging."""
    logger.info("Initializing %s v%s in %s mode", settings.PROJECT_NAME, settings.VERSION, settings.APP_ENV)
    logger.info("CORS origins configured: %s", settings.cors_origin_list)
    logger.info("Embedding model selection status: %s", settings.embedding_selection_status)
    yield
    logger.info("Shutting down %s", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Discovery Engine & Grounded Qualitative Research Intelligence API. "
        "Engineering specification: part1_discovery_engine_implementation_spec.md"
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Strict CORS configuration (Whitelisted origins only, no wildcard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_v1_router)


@app.get("/", response_model=Dict[str, Any])
async def root() -> Dict[str, Any]:
    """Root endpoint verifying API server is operational."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/docs",
        "health_endpoint": "/api/v1/health",
        "status": "operational",
    }
