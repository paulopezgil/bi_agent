# Implementation Instructions

You are an expert AI Engineer. Your goal is to build the "Autonomous BI Analyst" following the docs in this folder.

## Current Project State (Important)
- The repo is already containerized with:
	- root `docker-compose.yml`
	- `docker/agent/Dockerfile`
	- `docker/mcp/Dockerfile`
	- `docker/postgres/init.sql`
- `pyproject.toml` exists with baseline dependencies.
- `src/main.py` and `src/mcp_server/server.py` are currently placeholders.
- Do not re-scaffold structure unless explicitly asked.

## Phase 1: Environment
- Initialize a Python 3.11+ project using `uv`.
- Install `langgraph`, `mcp`, `langchain-openai` (or anthropic), and `psycopg2-binary`.
- Ensure `uv.lock` is generated and committed.

## Phase 2: MCP Server
- Build the server in `src/mcp_server/server.py`.
- Ensure the `execute_readonly_query` tool handles Postgres exceptions gracefully.
- Enforce read-only query behavior with explicit statement validation and/or transaction safety.

## Phase 3: LangGraph
- Implement the graph in `src/agent/graph.py`.
- Add a "self-correction" loop: if the SQL fails, the agent must use the error message to fix the query.
- Keep `AgentState` immutable in all node returns.

## Phase 4: Main Entry
- Create `src/main.py` to initialize the MCP client, connect it to the LangGraph agent, and start a REPL chat interface.

## Phase 5: Quality Gates
- Add tests under `tests/` for MCP tools and retry loop behavior.
- Add lint/type/test commands for local and CI execution.