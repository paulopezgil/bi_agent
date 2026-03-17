from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extensions import connection


def build_database_url() -> str:
    """Build a PostgreSQL connection URL from environment variables."""
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    host = os.getenv("PGHOST", "postgres")
    port = os.getenv("PGPORT", "5432")
    dbname = os.getenv("PGDATABASE", "bi_analytics")
    user = os.getenv("PGUSER", "bi_readonly")
    password = os.getenv("PGPASSWORD", "bi_readonly_pass")
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


@contextmanager
def get_connection() -> Generator[connection, None, None]:
    """Create and close a PostgreSQL connection."""
    conn = psycopg2.connect(build_database_url(), connect_timeout=5)
    try:
        yield conn
    finally:
        conn.close()
