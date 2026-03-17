from __future__ import annotations

from backend.postgres.connection import build_database_url as _build_database_url


def build_database_url() -> str:
    """Backward-compatible wrapper for database URL builder."""
    return _build_database_url()
