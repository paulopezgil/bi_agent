# Autonomous BI Analyst

A production-grade AI analyst agent built with LangGraph and MCP to answer natural-language questions against PostgreSQL, including self-healing SQL generation.

## Current Status

- Dockerized 3-service stack is scaffolded (`agent`, `mcp`, `postgres`).
- Project packaging is initialized with `pyproject.toml`.
- Postgres demo schema and seed data are provisioned via `docker/postgres/init.sql`.
- Runtime entrypoints are placeholders pending full LangGraph and MCP implementations.

## Goals

- Convert user questions into safe SQL queries.
- Query PostgreSQL through an MCP server boundary.
- Recover from SQL errors using an automated correction loop.

## Architecture Summary

- `src/agent/`: LangGraph orchestration and node logic.
- `src/mcp_server/`: MCP server exposing PostgreSQL tools.
- `src/shared/`: Shared typed models and utilities.
- `tests/`: Pytest suite for graph nodes and MCP tools.
- `docker/agent/Dockerfile`: container image for LangGraph agent runtime.
- `docker/mcp/Dockerfile`: container image for MCP server runtime.
- `docker/postgres/init.sql`: local DB schema + seed data for demos.

Key rules:
- Strict typing with Python type hints and Pydantic models.
- Agent and DB credentials remain separated (agent uses MCP only).
- Agent state updates should be immutable (return new state from nodes).
- Use `uv` for Python dependency and lockfile management.

## Planned Graph Flow

1. `planner`: Detect intent and whether DB access is needed.
2. `get_schema`: Fetch table metadata through MCP tools.
3. `sql_generator`: Generate SQL from intent + schema context.
4. `execute_query`: Run query via MCP `execute_readonly_query` tool.
5. `error_handler`: On DB error, increment retry count and feed error back.
6. `should_continue`: Stop or retry (max 3 retries).

## MCP Tools (Planned)

- `list_tables`: list table names in the `public` schema.
- `describe_table(table_name: str)`: return columns, types, and FK relationships.
- `execute_readonly_query(query: str)`: run read-only SQL and return JSON rows or clear errors.

## Docker Layout

```text
ai-analyst-agent/
├── docker-compose.yml
├── .env
├── src/
├── docker/
│   ├── agent/Dockerfile
│   ├── mcp/Dockerfile
│   └── postgres/init.sql
└── pyproject.toml
```

Services:
- `postgres`: local PostgreSQL with demo schema/seed
- `mcp`: MCP server runtime
- `agent`: LangGraph agent runtime

Run locally:

```bash
docker compose up -d --build
```

Stop:

```bash
docker compose down
```

The MCP server should connect using the `PG*` variables (`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`).

## Implementation Roadmap

1. Environment and tooling:
	- initialize `uv` project workflow (`uv.lock`, command docs)
	- wire lint/type/test commands in CI
2. MCP server implementation (`src/mcp_server/server.py`):
	- implement `list_tables`, `describe_table`, `execute_readonly_query`
	- enforce read-only safety and graceful Postgres error handling
3. LangGraph implementation (`src/agent/graph.py`):
	- implement nodes `planner`, `get_schema`, `sql_generator`, `execute_query`, `error_handler`
	- implement retry loop (`retry_count` max 3) based on SQL error feedback
4. App entrypoint (`src/main.py`):
	- initialize MCP client
	- run REPL chat loop against graph
5. Tests:
	- unit tests for MCP tool behavior and edge cases
	- graph tests for success path, retry path, and max-retry exit
