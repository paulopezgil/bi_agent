from __future__ import annotations

from psycopg2.extras import RealDictCursor

from backend.core.schemas import ToolResponse
from backend.mcp.utils import handle_tool_exception
from backend.postgres.connection import get_connection


def run_execute_readonly_query(query: str) -> ToolResponse:
    try:
        sql = query.strip()

        with get_connection() as conn:
            conn.autocommit = False
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                rows = [dict(row) for row in cur.fetchall()] if cur.description else []
                conn.rollback()

        return ToolResponse(ok=True, data={"rows": rows, "row_count": len(rows)})
    except Exception as exc:
        return handle_tool_exception(exc)
