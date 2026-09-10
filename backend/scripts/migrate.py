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

from sqlalchemy import create_engine, inspect, text
from alembic.config import Config
from alembic import command

from app.core.config import settings


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        # current_schema() is the FIRST schema on search_path with CREATE
        # rights - i.e. exactly where an unqualified CREATE TABLE lands.
        # has_table() with no schema= instead checks the whole search_path,
        # which is wrong the moment another schema (e.g. a shared Postgres
        # instance's `public`, kept on the path for extension functions
        # like uuid_generate_v4()) also happens to contain a same-named
        # table belonging to a completely different application.
        target_schema = conn.execute(text("SELECT current_schema()")).scalar()
    inspector = inspect(engine)
    has_alembic_table = inspector.has_table("alembic_version", schema=target_schema)
    has_app_tables = inspector.has_table("users", schema=target_schema)
    engine.dispose()
    print(f"[migrate] target schema: {target_schema}", file=sys.stderr)

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
