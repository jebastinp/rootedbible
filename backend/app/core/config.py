"""
Application configuration loaded from environment variables (.env).
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 120

    # Church defaults
    CHURCH_NAME: str = "Rooted Church"
    READING_YEAR: int = 2026


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
