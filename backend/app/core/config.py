"""
Application configuration loaded from environment variables (.env).
"""
from functools import lru_cache
import json
from typing import Any, List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", enable_decoding=False)

    # App
    APP_NAME: str = "Rooted - Bible Reading Tracker API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Security
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_super_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days - members stay logged in
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # Supabase Auth (Google sign-in is handled by Supabase, not verified directly
    # against Google). This IS a secret - find it in Supabase Dashboard ->
    # Project Settings -> API -> JWT Settings -> JWT Secret. Used to verify the
    # session token the frontend gets back from supabase-js after OAuth.
    SUPABASE_JWT_SECRET: str = ""

    # Database (Supabase Postgres connection string)
    # postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/rooted"

    # Supabase (optional direct usage from frontend / storage)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:4173"]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: Any) -> Any:
        # Some hosts (Railway's own Postgres plugin, older Heroku-style URLs)
        # hand out `postgres://` - SQLAlchemy 2.x only recognizes
        # `postgresql://` and raises NoSuchModuleError at engine-creation
        # time (i.e. at process startup, before anything can bind to $PORT).
        if isinstance(value, str) and value.startswith("postgres://"):
            return "postgresql://" + value[len("postgres://"):]
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> List[str]:
        if isinstance(value, list):
            return value
        if not isinstance(value, str) or not value.strip():
            return []
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(parsed, str):
            return [parsed]
        return parsed

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 120

    # Church defaults
    CHURCH_NAME: str = "Rooted Church"
    READING_YEAR: int = 2026


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
