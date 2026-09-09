from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException

from app.core.config import settings

# Supabase Postgres works fine with the standard psycopg2 sync driver.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"connect_timeout": 5},
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_db() -> Session:
    """FastAPI dependency that yields a DB session and always closes it."""
    if any(marker in settings.DATABASE_URL for marker in ("YOUR_PASSWORD", "YOUR_PROJECT", "[PASSWORD]", "[HOST]")):
        raise HTTPException(
            status_code=503,
            detail="Database setup is incomplete. Configure DATABASE_URL in backend/.env and run database/schema.sql in your database.",
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
