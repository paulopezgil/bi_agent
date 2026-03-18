# Autonomous BI Analyst

Autonomous BI Analyst is a full-stack prototype that combines:
- a LangGraph orchestration workflow,
- an MCP-style database tool server,
- PostgreSQL with seeded analytics data,
- and a Streamlit chatbot frontend.

## Repository Layout

```text
bi-agent/
├── docker-compose.yml
├── backend/
│   ├── agent/
│   │   ├── config/
│   │   │   ├── prompts.py
│   │   │   └── state.py
│   │   ├── nodes/
│   │   │   ├── guardrail.py
│   │   │   ├── query_database.py
│   │   │   ├── retry.py
│   │   │   ├── security_warning.py
│   │   │   └── summarize.py
│   │   ├── routers/
│   │   │   ├── guardrail.py
│   │   │   ├── query_database.py
│   │   │   └── tool_execution.py
│   │   ├── graph.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── mcp/
│   │   ├── client.py
│   │   ├── server.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── postgres/
│   │   └── init/
│   │       ├── 001_schema.sql
│   │       ├── 002_seed_data.sql
│   │       └── 003_roles.sql
│   ├── core/
│   │   ├── openai_client.py
│   │   └── schemas.py
│   └── utils/
│       └── parsing.py
├── frontend/
│   └── chatbot/
│       ├── app.py
│       ├── Dockerfile
│       └── requirements.txt
└── tests/
```

## Docker Services

`docker-compose.yml` currently defines four services:
- `postgres` on `5432`
- `mcp` as an internal service (exposes `8001` to the compose network)
- `agent` on `8000`
- `frontend` on `3000` (Streamlit container listens on `8501`)

## Current Agent Workflow

The LangGraph flow in `backend/agent/graph.py` is:

1. `guardrail`
2. route to `query_database` or `security_warning`
3. from `query_database`, route to `execute_tools` or finish
4. from `execute_tools`, route to `retry` or `summarize`
5. `retry` and `summarize` both return to `query_database`

### Prompt Configuration

Prompt text is centralized in `backend/agent/config/prompts.py`:
- `QUERY_DATABASE_SYSTEM_PROMPT`
- `GUARDRAIL_SYSTEM_PROMPT`

### Shared Tool Schema

`backend/core/schemas.py` defines `ToolResponse` to standardize tool output:
- `ok`
- `data`
- `error`
- `code`

## MCP Integration Mode

Current agent MCP integration uses stdio transport via `backend/mcp/client.py`.
The agent launches the MCP server process and loads tools with `langchain-mcp-adapters`.

## Important Runtime Notes

- The frontend currently posts to `POST /chat` on the agent URL.
- The agent Docker command currently runs `python -m backend.agent.graph`, which is graph compilation logic and not an HTTP API server.
- Because of that, the full frontend-to-agent API path is not yet finalized.

This repository is in active refactor, and orchestration structure is ahead of API wiring.

## Run with Docker Compose

```bash
docker compose up -d --build
```

Stop:

```bash
docker compose down
```

## Next Recommended Steps

1. Add a dedicated agent API entrypoint (FastAPI) that invokes the compiled graph and returns `answer/sql/retries/rows/error`.
2. Decide one MCP deployment mode and align compose plus client:
   - keep stdio subprocess mode, or
   - switch to internal network service mode (`agent -> mcp:8001`).
3. Add integration tests for end-to-end flow (`frontend -> agent -> mcp -> postgres`).
4. Update health endpoints and README examples once API wiring is complete.
