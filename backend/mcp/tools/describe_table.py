from __future__ import annotations

from psycopg2.extras import RealDictCursor

from backend.core.schemas import ToolResponse
from backend.mcp.utils import handle_tool_exception
from backend.postgres.connection import get_connection


def run_describe_table(table_name: str) -> ToolResponse:
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = %s
                    ORDER BY ordinal_position
                    """,
                    (table_name,),
                )
                columns = [dict(row) for row in cur.fetchall()]

                cur.execute(
                    """
                    SELECT
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                     AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                     AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND tc.table_schema = 'public'
                      AND tc.table_name = %s
                    ORDER BY kcu.column_name
                    """,
                    (table_name,),
                )
                foreign_keys = [dict(row) for row in cur.fetchall()]

        return ToolResponse(
            ok=True,
            data={
                "table_name": table_name,
                "columns": columns,
                "foreign_keys": foreign_keys,
            },
        )
    except Exception as exc:
        return handle_tool_exception(exc)
