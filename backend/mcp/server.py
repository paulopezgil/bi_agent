from __future__ import annotations

import psycopg2
from mcp.server.fastmcp import FastMCP
from psycopg2.extras import RealDictCursor

from backend.core.logger import get_logger
from backend.core.schemas import ToolResponse
from backend.postgres.connection import get_connection

logger = get_logger(__name__)
mcp = FastMCP("Postgres-Assistant")


@mcp.tool()
def list_tables() -> ToolResponse:
    """Return all tables in the public schema."""
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
    except psycopg2.Error as exc:
        logger.exception("list_tables failed")
        return ToolResponse(ok=False, error=str(exc), code=exc.pgcode)
    except Exception as exc:  # pragma: no cover - defensive normalization
        logger.exception("list_tables failed with unexpected error")
        return ToolResponse(ok=False, error=str(exc))


@mcp.tool()
def describe_table(table_name: str) -> ToolResponse:
    """Describe a table's columns and foreign keys."""
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
    except psycopg2.Error as exc:
        logger.exception("describe_table failed")
        return ToolResponse(ok=False, error=str(exc), code=exc.pgcode)
    except Exception as exc:  # pragma: no cover - defensive normalization
        logger.exception("describe_table failed with unexpected error")
        return ToolResponse(ok=False, error=str(exc))


@mcp.tool()
def execute_readonly_query(query: str) -> ToolResponse:
    """Execute SQL query. Validation is delegated upstream."""
    sql = query.strip()
    try:
        with get_connection() as conn:
            conn.autocommit = False
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                rows = [dict(row) for row in cur.fetchall()] if cur.description else []
                conn.rollback()

        return ToolResponse(ok=True, data={"rows": rows, "row_count": len(rows)})
    except psycopg2.Error as exc:
        logger.exception("execute_readonly_query failed")
        return ToolResponse(ok=False, error=str(exc), code=exc.pgcode)
    except Exception as exc:  # pragma: no cover - defensive normalization
        logger.exception("execute_readonly_query failed with unexpected error")
        return ToolResponse(ok=False, error=str(exc))


if __name__ == "__main__":
    logger.info("Starting Postgres-Assistant MCP server")
    mcp.run()
