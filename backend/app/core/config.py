"""
Application Configuration Module.

Loads configuration from environment variables or .env file.
Governed by: part1_discovery_engine_implementation_spec.md
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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

    # Embedding Model (Railway CPU Container) — Selection Pending Benchmark (Step 5)
    # No candidate is selected or defaulted during Step 1 foundation.
    EMBEDDING_MODEL_NAME: Optional[str] = None

    # CORS Allowed Origins
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def embedding_selection_status(self) -> str:
        return "selected" if self.EMBEDDING_MODEL_NAME else "pending_benchmark"


settings = Settings()
