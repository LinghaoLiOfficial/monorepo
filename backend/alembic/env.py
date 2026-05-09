import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def _to_sync_sqlalchemy_url(url: str) -> str:
    """Convert async SQLAlchemy URL to a sync URL for Alembic."""
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "+psycopg2", 1)
    return url


def _resolve_database_url() -> str:
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return _to_sync_sqlalchemy_url(env_url)
    return _to_sync_sqlalchemy_url(config.get_main_option("sqlalchemy.url"))


def run_migrations_offline() -> None:
    url = _resolve_database_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = _resolve_database_url()

    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
