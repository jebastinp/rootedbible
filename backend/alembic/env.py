import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import create_engine, pool
from alembic import context

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa
from app.db.base_class import Base  # noqa
from app import models  # noqa - ensures all models are registered on Base.metadata

config = context.config
# configparser's interpolation treats a bare `%` as the start of a
# `%(var)s` reference and raises on any URL containing one (a percent-
# encoded query string, e.g. `?options=-c%20search_path...`, or a password
# with a literal `%`) - `%%` is configparser's own escape for a literal `%`.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Built directly from settings.DATABASE_URL (not engine_from_config's
    # ini-parsed copy) so a literal `%` in the URL never has to round-trip
    # through configparser interpolation at all.
    connectable = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
