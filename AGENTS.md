# AGENTS.md - BI Agent Guide

Instructions for coding agents operating in this repository.
Apply these defaults unless a user request explicitly overrides them.

## Project Context

- App: Autonomous BI Analyst.
- Stack: FastAPI + LangGraph + MCP + PostgreSQL + Streamlit.
- Primary Python package: `backend/`.
- Tests: `tests/unit/` (mocked/offline) and `tests/integration/` (real provider calls).

## Repo Layout

- `backend/agent/`: API app, graph compile/wiring, nodes, routers, prompts, schemas.
- `backend/core/`: logging, shared schemas, LLM abstraction, engine factory/providers.
- `backend/mcp/`: MCP server, tool registration, DB tool implementations.
- `backend/postgres/init/`: SQL schema and seed scripts.
- `frontend/chatbot/`: Streamlit chat UI.
- `tests/unit/`: node-level, graph-level, and MCP unit tests.
- `tests/integration/llm/`: OpenAI/Anthropic/Azure engine integration checks.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

## Build and Run Commands

### Docker workflow

```bash
docker compose up -d --build
docker compose down
```

### Run services directly

```bash
# FastAPI agent
uvicorn backend.agent.app:app --reload --host 0.0.0.0 --port 8000

# MCP server
python -m backend.mcp.server

# Streamlit frontend
streamlit run frontend/chatbot/app.py --server.port 3000
```

## Lint, Format, Typecheck

```bash
ruff check .
ruff format .
mypy backend tests
```

Notes:
- Ruff line length is 100.
- Mypy is strict (`strict = true`).

## Test Commands

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest -m integration

# Exclude integration tests
pytest -m "not integration"
```

### Single-test patterns (important)

```bash
# Single file
pytest tests/unit/agent/nodes/test_query_database.py

# Single test function
pytest tests/unit/agent/nodes/test_query_database.py::test_returns_engine_response_as_message

# Subset by keyword
pytest tests/unit/agent/nodes/test_query_database.py -k "retry"

# Stop quickly while iterating
pytest tests/unit/agent/nodes/test_query_database.py -x
```

## Environment Variables

- `LLM_ENGINE` (`langchain-openai`, `langchain-anthropic`, `langchain-azure-openai`).
- OpenAI: `OPENAI_API_KEY`, optional `OPENAI_MODEL`.
- Anthropic: `ANTHROPIC_API_KEY`, optional `ANTHROPIC_MODEL`.
- Azure: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, optional `AZURE_OPENAI_API_VERSION`.
- `MCP_BASE_URL` (default `http://mcp:8001/mcp`).
- `AGENT_BASE_URL` for frontend -> agent calls.

## Code Style and Conventions

### Imports

- Prefer absolute imports from `backend...`.
- Order groups as stdlib, third-party, local.
- Keep imports explicit; avoid wildcard imports.

### Formatting and organization

- Follow Ruff formatting and 100-char lines.
- Keep functions small and focused.
- Extract helpers for parsing/normalization.
- Add comments only for non-obvious behavior.

### Typing (repo-specific rules)

- Use built-in containers: `list`, `dict`, `tuple`, `set`.
- Use `X | None`, not `Optional[X]`.
- Do not use `Any`.
- For mixed/unknown mappings, use plain `dict`/`list`.
- Do not import `Dict`, `List`, `Optional`, `Any` from `typing`.
- Avoid variable assignment annotations (except schema/model field needs).

### Naming

- Modules/files: `snake_case.py`.
- Functions/variables: `snake_case`.
- Classes/models: `PascalCase`.
- Constants and prompt constants: `UPPER_SNAKE_CASE`.
- Node builders follow existing `make_*` naming pattern.

### Error handling

- Validate early at boundaries.
- In graph nodes, fail safely and return explicit fallback state when needed.
- Log with contextual messages via `get_logger(__name__)`.
- Preserve actionable user errors; keep stack details in logs.
- Never silently swallow exceptions.

### Testing guidance

- Prefer unit tests for behavior/routing changes.
- Mock engine/tool boundaries in unit tests.
- Update graph-level tests for retry/edge changes.
- Keep integration tests focused on provider compatibility.

## Design Principles for Agent Changes

When designing or refactoring, explicitly apply:

- Single Responsibility.
- Separation of Concerns.
- Dependency Inversion.
- Open/Closed Principle.
- DRY without premature abstraction.
- Explicit over implicit.
- Fail fast.
- Low coupling and high cohesion.

In architecture discussions, include trade-offs, not just one "correct" answer.

## Collaboration Pattern

For non-trivial tasks:

1. Restate objective and propose a concise plan.
2. Implement in small, reviewable steps.
3. Run relevant lint/type/test commands.
4. Report what changed and why.

## Cursor/Copilot Rule Files

Checked and not found in this repository:

- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`

No additional Cursor or Copilot instruction files are currently present.
