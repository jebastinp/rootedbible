"""
Deploy-time migration entrypoint (run on every container start).

Handles the one-time bootstrap case where a database's schema was already
created directly from database/schema.sql or supabase/schema.sql - e.g. a
Supabase project set up by hand, which is exactly how this app documents
first-time setup. In that case `alembic upgrade head` starting from empty
migration history tries to CREATE TYPE/CREATE TABLE objects that already
exist and fails outright (psycopg2.errors.DuplicateObject).

If we detect that shape - no `alembic_version` table yet, but the app's
own tables already exist - we stamp the database at head instead of
replaying migrations (schema.sql is kept in lockstep with every migration
in this repo, so "already has the users table" really does mean "already
at head"), then run upgrade normally, which becomes a no-op for that case
and still applies forward for any migration added since.

Usage:
    python scripts/migrate.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine, inspect
from alembic.config import Config
from alembic import command

from app.core.config import settings


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    has_alembic_table = inspector.has_table("alembic_version")
    has_app_tables = inspector.has_table("users")
    engine.dispose()

    cfg = Config(str(backend_dir / "alembic.ini"))

    if not has_alembic_table and has_app_tables:
        print(
            "[migrate] alembic_version is missing but the 'users' table already "
            "exists - this database was bootstrapped from schema.sql. Stamping "
            "at head instead of replaying migrations from scratch.",
            file=sys.stderr,
        )
        command.stamp(cfg, "head")

    command.upgrade(cfg, "head")
    print("[migrate] database is at head.", file=sys.stderr)


if __name__ == "__main__":
    main()
