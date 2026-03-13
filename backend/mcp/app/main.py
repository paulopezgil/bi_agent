from __future__ import annotations

import os
import re
from contextlib import contextmanager
from typing import Any

import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor

app = FastAPI(title="MCP SQL Tools", version="0.1.0")

FORBIDDEN_SQL_RE = re.compile(
    r"\b(insert|update|delete|alter|drop|truncate|create|grant|revoke|comment|copy|call|do)\b",
    re.IGNORECASE,
)
ALLOWED_PREFIX_RE = re.compile(r"^\s*(select|with|show|explain)\b", re.IGNORECASE)


class TableRequest(BaseModel):
    table_name: str


class QueryRequest(BaseModel):
    query: str


def db_config() -> dict[str, Any]:
    return {
        "host": os.getenv("PGHOST", "postgres"),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.getenv("PGDATABASE", "bi_analytics"),
        "user": os.getenv("PGUSER", "bi_readonly"),
        "password": os.getenv("PGPASSWORD", "bi_readonly_pass"),
        "connect_timeout": 5,
    }


@contextmanager
def get_connection() -> Any:
    conn = psycopg2.connect(**db_config())
    try:
        yield conn
    finally:
        conn.close()


def validate_read_only_query(query: str) -> str | None:
    candidate = query.strip().rstrip(";")
    if not candidate:
        return "Query cannot be empty."
    if ";" in candidate:
        return "Multiple SQL statements are not allowed."
    if FORBIDDEN_SQL_RE.search(candidate):
        return "Only read-only SQL statements are allowed."
    if not ALLOWED_PREFIX_RE.match(candidate):
        return "Only SELECT/WITH/SHOW/EXPLAIN statements are allowed."
    return None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "mcp"}


@app.post("/tools/list_tables")
def list_tables() -> dict[str, Any]:
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
                rows = [r[0] for r in cur.fetchall()]
        return {"ok": True, "tables": rows}
    except psycopg2.Error as exc:
        return {"ok": False, "error": str(exc), "code": exc.pgcode}


@app.post("/tools/describe_table")
def describe_table(payload: TableRequest) -> dict[str, Any]:
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
                    (payload.table_name,),
                )
                columns = [dict(r) for r in cur.fetchall()]

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
                    (payload.table_name,),
                )
                foreign_keys = [dict(r) for r in cur.fetchall()]

        return {
            "ok": True,
            "table_name": payload.table_name,
            "columns": columns,
            "foreign_keys": foreign_keys,
        }
    except psycopg2.Error as exc:
        return {"ok": False, "error": str(exc), "code": exc.pgcode}


@app.post("/tools/execute_readonly_query")
def execute_readonly_query(payload: QueryRequest) -> dict[str, Any]:
    validation_error = validate_read_only_query(payload.query)
    if validation_error:
        return {"ok": False, "error": validation_error, "code": None}

    query = payload.query.strip().rstrip(";")

    try:
        with get_connection() as conn:
            conn.autocommit = False
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SET TRANSACTION READ ONLY")
                cur.execute(query)
                rows = [dict(r) for r in cur.fetchall()] if cur.description else []
                conn.rollback()
        return {"ok": True, "rows": rows, "row_count": len(rows)}
    except psycopg2.Error as exc:
        return {"ok": False, "error": str(exc), "code": exc.pgcode}
