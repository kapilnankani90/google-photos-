"""
Application Configuration Module.

Loads configuration from environment variables or .env file.
Governed by: part1_discovery_engine_implementation_spec.md
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application Information
    PROJECT_NAME: str = "Google Photos Discovery Engine"
    VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    PORT: int = 8000

    # Database Configuration (Supabase PostgreSQL + pgvector) — Scheduled for Step 2
    DATABASE_URL: Optional[str] = None

    # Server-Side AI (Google Gemini) — Scheduled for Step 7
    GEMINI_API_KEY: Optional[str] = None

    # Server-Side NLU (Groq LLM for Memory Search MVP)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL_NAME: str = "qwen/qwen3.8-27b"
    GROQ_TIMEOUT_SECONDS: float = 12.0

    # D1 Discovery Engine API Endpoint (for D2 HTTP consumption)
    DISCOVERY_ENGINE_URL: str = "http://localhost:8000"

    # Retrieval Configuration (Step 6 / Section 24 Fallback)
    # Active fallback following Step 5 NO_ELIGIBLE_CANDIDATE determination
    RETRIEVAL_MODE: str = "lexical_fts"

    # Embedding Model (Railway CPU Container)
    # Model loading is disabled when RETRIEVAL_MODE == "lexical_fts" or when unset.
    EMBEDDING_MODEL_NAME: Optional[str] = None

    # CORS Allowed Origins
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,https://google-photos-d1.vercel.app"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def embedding_selection_status(self) -> str:
        if (
            self.RETRIEVAL_MODE == "lexical_fts"
            or not self.EMBEDDING_MODEL_NAME
            or self.EMBEDDING_MODEL_NAME.strip().lower() in ("none", "null", "disabled")
        ):
            return "lexical_fts_fallback"
        return "selected"


settings = Settings()

