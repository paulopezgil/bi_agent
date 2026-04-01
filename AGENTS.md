# AGENTS.md - BI Agent Guide

Instructions for coding agents operating in this repository. Apply these defaults unless requested otherwise.

## Project Context
- **App**: Autonomous BI Analyst
- **Stack**: FastAPI, LangGraph, MCP, PostgreSQL, Streamlit
- **Codebase**: `backend/` (API, graph, tools), `frontend/` (UI), `tests/` (unit and integration)

## Build, Run, and Lint Commands

### Docker (Full Stack)
```bash
docker compose up -d --build
docker compose down
```

### Local Services
```bash
uvicorn backend.agent.app:app --reload --host 0.0.0.0 --port 8000  # FastAPI agent
python -m backend.mcp.server                                       # MCP server
streamlit run frontend/chatbot/app.py --server.port 3000           # UI
```

### Linting & Typechecking
```bash
ruff check .      # Lint (100 char limit)
ruff format .     # Format
mypy backend tests # Typecheck (strict = true)
```

## Testing Commands

Always run tests to verify changes.
```bash
pytest                                                # All tests
pytest tests/unit/                                    # Unit tests only
pytest -m integration                                 # Integration tests only
pytest -m "not integration"                           # Exclude integration tests
```

### Single-Test Execution Patterns (CRITICAL)
When iterating on a specific feature, run targeted tests:
```bash
pytest tests/unit/agent/nodes/test_query_database.py                                  # Entire file
pytest tests/unit/agent/nodes/test_query_database.py::test_returns_message            # Single function
pytest tests/unit/agent/nodes/test_query_database.py -k "retry"                       # By keyword
pytest tests/unit/agent/nodes/test_query_database.py -x                               # Fail fast
```

## Code Style & Conventions

### Imports & Formatting
- **Imports**: Prefer absolute (`from backend...`), avoid wildcards (`*`). Group: stdlib, 3rd-party, local.
- **Formatting**: Ruff, 100-character line length limit. Extract helpers for complex parsing logic.

### Typing (Strict Rules)
- **Use built-ins**: `list`, `dict`, `tuple`, `set`. (No `typing.List`, `typing.Dict`).
- **Optionals**: Use `X | None`, NOT `Optional[X]`.
- **Avoid `Any`**: For unknown structures, use plain `dict` or `list`.
- **Variables**: Avoid assigning type annotations to variables unless required by Pydantic models.

### Naming
- **Files/Variables/Functions**: `snake_case`
- **Classes/Models**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Node Builders**: `make_*` prefix pattern.

### Error Handling
- **Boundaries**: Validate inputs early (API bounds, tools).
- **Nodes**: Fail safely, return explicit fallback states in graph nodes.
- **Logging**: Use contextual messages via `get_logger(__name__)`. Keep stack traces in logs, not UI.
- **No Swallowing**: Never use empty `except:` or `pass` exceptions silently.

## Agent Workflow & Design Principles

### Design Principles
Apply Single Responsibility, Separation of Concerns, Dependency Inversion, Open/Closed, and DRY. Prefer explicit logic over implicit magic. Aim for low coupling and high cohesion.

### Collaboration Pattern
1. Restate the objective and propose a concise plan.
2. Implement in small, verifyable steps.
3. Run relevant lint, type, and test commands immediately after implementation.
4. Report changes succinctly without over-explaining code unless requested.

## External Rules (Cursor / Copilot)
No external rule files were found in this repository. Do not look for or rely on:
- `.cursor/rules/`
- `.cursorrules`
- `.github/copilot-instructions.md`
