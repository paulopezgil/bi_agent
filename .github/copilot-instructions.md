# Implementation Instructions

You are an expert AI Engineer. Build and evolve the Autonomous BI Analyst in its current full-stack shape.

## Current Project State (Important)
- Orchestration: root `docker-compose.yml`.
- Services and Dockerfiles:
  - `backend/agent/Dockerfile`
  - `backend/mcp/Dockerfile`
  - `frontend/chatbot/Dockerfile`
- Postgres init scripts:
  - `backend/postgres/init/001_schema.sql`
  - `backend/postgres/init/002_seed_data.sql`
  - `backend/postgres/init/003_roles.sql`
- Implemented APIs:
  - Agent: `backend/agent/app/main.py` (`POST /chat`)
  - MCP: `backend/mcp/app/main.py` (tool endpoints)
- Current frontend:
  - `frontend/chatbot/index.html`
  - `frontend/chatbot/styles.css`
  - `frontend/chatbot/app.js`

## Phase 1: Stabilize Runtime
- Ensure `docker compose up -d --build` brings all 4 services up cleanly.
- Keep service URLs/ports consistent:
  - frontend: `3000`
  - agent: `8000`
  - mcp: `8001`
  - postgres: `5432`

## Phase 2: Agent Quality
- Improve SQL generation beyond rule-based mapping.
- Keep self-correction loop with max 3 retries.
- Preserve clear response payloads (`answer`, `sql`, `retries`, `rows`, `error`).

## Phase 3: MCP Hardening
- Preserve read-only validation and transaction safety.
- Expand table metadata and error normalization behavior.
- Add tests for blocked write SQL and DB error scenarios.

## Phase 4: Frontend UX
- Keep a simple chatbot UI with clear query/result visibility.
- Surface generated SQL and retry count for transparency.
- Ensure responsive behavior on mobile and desktop.

## Phase 5: Engineering Quality
- Add lint/type/test commands and CI workflow.
- Add integration tests for `agent <-> mcp <-> postgres`.
- Document deployment and environment setup in `README.md`.
