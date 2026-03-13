# Autonomous BI Analyst

Full-stack prototype of an AI analyst system with:
- a LangGraph-based backend agent,
- an MCP-like SQL tools service,
- PostgreSQL with seeded BI data,
- a Streamlit chatbot UI.

## Current Architecture

```text
bi-agent/
├── docker-compose.yml
├── .env
├── backend/
│   ├── agent/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       ├── main.py
│   │       └── graph.py
│   ├── mcp/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── app/
│   │       └── main.py
│   └── postgres/
│       └── init/
│           ├── 001_schema.sql
│           ├── 002_seed_data.sql
│           └── 003_roles.sql
└── frontend/
    └── chatbot/
        ├── Dockerfile
        ├── requirements.txt
        └── app.py
```

## Services

- `postgres` (`:5432`): database with schema, seed data, and read-only role.
- `mcp` (`:8001`): SQL tools API.
- `agent` (`:8000`): LangGraph orchestration API (`/chat`).
- `frontend` (`:3000`): Streamlit chatbot web app.

## Agent Flow

1. Build SQL from user question.
2. Execute read-only query through MCP service.
3. If SQL fails, retry with corrected/fallback SQL (max 3 retries).
4. Return answer + SQL + retries + rows.

## MCP Tools Endpoints

- `POST /tools/list_tables`
- `POST /tools/describe_table`
- `POST /tools/execute_readonly_query`

Safety behavior:
- Rejects write/DDL statements.
- Rejects multiple statements.
- Executes under read-only transaction.
- Returns structured errors with DB code when available.

## Run Locally

```bash
docker compose up -d --build
```

Open:
- Frontend: `http://localhost:3000`
- Agent health: `http://localhost:8000/health`
- MCP health: `http://localhost:8001/health`

Stop:

```bash
docker compose down
```

## Next Steps

1. Replace rule-based SQL generation with an LLM planner/generator.
2. Swap MCP HTTP shim for official MCP transport wiring end-to-end.
3. Add integration tests for agent<->mcp<->postgres flow.
4. Add auth, CORS restrictions, and production-grade observability.
