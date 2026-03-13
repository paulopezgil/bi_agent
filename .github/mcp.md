# MCP Service Specification (Current HTTP Shim)

## Current Implementation Location
- `backend/mcp/app/main.py`

## Service Contract
- Health: `GET /health`
- Tools:
  - `POST /tools/list_tables`
  - `POST /tools/describe_table`
  - `POST /tools/execute_readonly_query`

## Behavior Requirements
1. Reject non-read-only SQL (`INSERT`, `UPDATE`, `DELETE`, DDL, etc.).
2. Reject multiple statements in one request.
3. Execute under read-only transaction semantics.
4. Return structured payloads (`ok`, `error`, `code`, `rows`, etc.).

## Database Connectivity
Uses env vars:
- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`

## Next Step
Migrate this HTTP shim to official MCP SDK transport while preserving the same tool behavior and safety guarantees.
