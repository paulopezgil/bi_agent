from __future__ import annotations

from backend.core.schemas import ToolResponse
from backend.mcp.core.exception_handling import handle_tool_exception
from backend.postgres.connection import get_connection


def run_list_tables() -> ToolResponse:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                    """
                )
                tables = [row[0] for row in cur.fetchall()]

        return ToolResponse(ok=True, data={"tables": tables})
    except Exception as exc:
        return handle_tool_exception(exc)
