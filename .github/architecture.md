# Project Architecture & Rules

## Overview
A full-stack Autonomous BI Analyst prototype with four containers:
- `postgres`: seeded analytics database
- `mcp`: SQL tools service
- `agent`: LangGraph orchestration API
- `frontend`: chatbot UI

## Current Directory Structure
- `backend/agent/`: LangGraph API service (`FastAPI`) and graph logic.
- `backend/mcp/`: SQL tools API (`FastAPI`) for schema/query operations.
- `backend/postgres/init/`: ordered SQL init scripts (`001`, `002`, `003`).
- `frontend/chatbot/`: static web UI served by Nginx.
- `docker-compose.yml`: local orchestration for all services.

## Runtime Wiring
1. Frontend calls `agent` at `POST /chat`.
2. Agent builds SQL and calls MCP endpoint `POST /tools/execute_readonly_query`.
3. MCP executes read-only SQL against Postgres and returns rows/errors.
4. Agent retries failed SQL up to 3 times and returns final response.

## Key Principles
1. **Read-Only Safety**: All agent-originated SQL must stay read-only.
2. **Isolation**: DB access happens through MCP service boundary.
3. **Immutability**: Graph nodes should return new state objects.
4. **Container Clarity**: Each service owns its own Dockerfile and dependencies.

## Immediate Priorities
1. Replace rule-based SQL generation with LLM-guided SQL planning.
2. Convert MCP HTTP shim to official MCP transport end-to-end.
3. Add integration tests across `frontend -> agent -> mcp -> postgres`.
4. Add CI checks for lint/type/test and container build verification.
