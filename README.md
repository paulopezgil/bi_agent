# Autonomous BI Analyst

Autonomous BI Analyst is a full-stack prototype that turns natural-language questions into SQL, executes them safely against a PostgreSQL analytics database, and returns a human-readable answer. It combines:

- a **LangGraph** orchestration workflow (the agent),
- a **Model Context Protocol (MCP)** database tool server,
- **PostgreSQL** with seeded analytics data,
- and a **Streamlit** chatbot frontend.

---

## Repository Layout

```text
bi-agent/
├── docker-compose.yml
├── backend/
│   ├── agent/                        # LangGraph agent (FastAPI + graph)
│   │   ├── api/
│   │   │   ├── routes.py             # POST /chat endpoint
│   │   │   └── schemas.py            # Request / response Pydantic models
│   │   ├── config/
│   │   │   ├── prompts.py            # Centralised prompt strings
│   │   │   └── state.py              # AgentState TypedDict
│   │   ├── nodes/                    # One function per graph node
│   │   │   ├── guardrail.py
│   │   │   ├── handle_tool_result.py
│   │   │   ├── query_database.py
│   │   │   ├── retry.py
│   │   │   ├── security_warning.py
│   │   │   └── summarize.py
│   │   ├── routers/                  # LangGraph conditional edge functions
│   │   │   ├── guardrail.py
│   │   │   ├── query_database.py
│   │   │   └── tool_execution.py
│   │   ├── graph.py                  # Graph compilation
│   │   ├── app.py                    # FastAPI application factory
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── core/
│   │   ├── llm/                      # Provider-agnostic LLM abstraction
│   │   │   ├── base.py               # LLMEngine abstract base class
│   │   │   ├── factory.py            # EngineFactory registry
│   │   │   └── engines/
│   │   │       ├── langchain_anthropic.py      # Claude via LangChain
│   │   │       ├── langchain_azure_openai.py  # Azure OpenAI via LangChain
│   │   │       └── langchain_openai.py         # GPT via LangChain
│   │   ├── logger.py
│   │   ├── openai_client.py
│   │   └── schemas.py                # Shared ToolResponse schema
│   ├── mcp/                          # MCP tool server (streamable HTTP)
│   │   ├── tools/
│   │   │   ├── describe_table.py
│   │   │   ├── execute_readonly_query.py
│   │   │   └── list_tables.py
│   │   ├── client.py                 # Tool loader + cache
│   │   ├── server.py                 # FastMCP server entrypoint
│   │   ├── utils.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── postgres/
│   │   └── init/
│   │       ├── 001_schema.sql
│   │       ├── 002_seed_data.sql
│   │       └── 003_roles.sql
│   └── utils/
│       └── parsing.py
├── frontend/
│   └── chatbot/
│       ├── app.py
│       ├── Dockerfile
│       └── requirements.txt
└── tests/
    ├── integration/
    │   └── llm/
    │       ├── test_anthropic_engine.py    # Live API tests for Anthropic engine
    │       ├── test_azure_openai_engine.py # Live API tests for Azure OpenAI engine
    │       └── test_openai_engine.py       # Live API tests for OpenAI engine
    └── unit/
        ├── agent/
        │   └── test_graph_retry.py
        └── mcp/
            └── test_mcp_server.py
```

---

## Docker Services

`docker-compose.yml` defines four services:

| Service    | Port  | Description                          |
|------------|-------|--------------------------------------|
| `postgres` | 5432  | Analytics database                   |
| `mcp`      | 8001  | MCP tool server (internal network)   |
| `agent`    | 8000  | LangGraph agent + FastAPI API        |
| `frontend` | 3000  | Streamlit chatbot                    |

```bash
# Start all services
docker compose up -d --build

# Stop
docker compose down
```

---

## Agent Workflow

The LangGraph flow in `backend/agent/graph.py`:

1. **`guardrail`** — classifies whether the request is safe to process
2. route → `query_database` or `security_warning`
3. **`query_database`** — generates SQL and calls the MCP tool
4. route → `execute_tools` or finish
5. **`handle_tool_result`** — inspects tool output for Postgres errors
6. route → `retry` (up to 3×) or `summarize`
7. **`summarize`** — turns query results into a natural-language answer

---

## LLM Engine Layer

`backend/core/llm/` provides a provider-agnostic abstraction over LLM calls used throughout the agent.

### How it works

`LLMEngine` (in `base.py`) defines a single async method:

```python
async def generate(output_schema, prompt_template, inputs) -> dict
```

Callers pass a Pydantic schema, a prompt template, and input values. They always receive a plain `dict` back — no provider types leak out.

`EngineFactory` (in `factory.py`) maps string keys to concrete engine classes:

```python
engine = EngineFactory.create("langchain-anthropic")  # or "langchain-openai"
result = await engine.generate(MySchema, "Analyse: {text}", {"text": "..."})
```

### Supported engines

| Key                      | Class                          | Default model / deployment         |
|--------------------------|--------------------------------|------------------------------------|
| `langchain-openai`       | `LangChainOpenAIEngine`        | `OPENAI_MODEL` / `gpt-4o`          |
| `langchain-anthropic`    | `LangChainAnthropicEngine`     | `ANTHROPIC_MODEL` / `claude-sonnet-4-6` |
| `langchain-azure-openai` | `LangChainAzureOpenAIEngine`   | `AZURE_OPENAI_DEPLOYMENT`          |

### Environment variables

```env
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o                  # optional

ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-sonnet-4-6    # optional

AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview   # optional
```

---

## Local Development & Testing

### Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

This installs the full runtime and all dev dependencies (`pytest`, `pytest-asyncio`, `python-dotenv`) in one step.

### Environment variables

Copy `.env.example` to `.env` and fill in your API keys (the file is gitignored):

```bash
cp .env.example .env
```

### Running the tests

```bash
# All tests
pytest

# Integration tests only (make real API calls — requires valid keys in .env)
pytest -m integration

# Skip integration tests
pytest -m "not integration"
```

Integration tests are in `tests/integration/llm/` — one file per engine — and verify that each one (`langchain-openai`, `langchain-anthropic`, `langchain-azure-openai`) can produce structured output from a live API call. Each engine has an easy test (maths question with a definitive answer) and a difficult test (open-ended question that validates structure only).

---

## Architecture & Design Principles

This codebase is designed to remain understandable and extensible as it grows. The decisions below are deliberate applications of standard software design principles.

### Single Responsibility

Every module has one reason to change. Graph nodes (`nodes/`) only transform agent state. Routers (`routers/`) only decide which edge to take. Prompt text lives exclusively in `config/prompts.py`. If the prompt for a node changes, only that file changes — nothing else.

### Open/Closed — the LLM engine registry

`EngineFactory` uses a registry dict to map string keys to engine classes. Adding a new LLM provider (e.g. Google Gemini) means:

1. Create `engines/langchain_google.py` implementing `LLMEngine`.
2. Add one line to the registry in `factory.py`.

No existing code is modified. Callers that already use `EngineFactory.create(...)` are unaffected.

### Dependency Inversion

Nodes and services depend on the `LLMEngine` abstraction, never on `ChatOpenAI` or `ChatAnthropic` directly. The concrete engine is injected at the call site via `EngineFactory`. This means the guardrail node, the summariser, and any future node can be tested with a mock engine that implements the same interface — no real API calls required.

### Interface Segregation

`LLMEngine` exposes exactly one method (`generate`). Engines are not forced to implement streaming, fine-tuning configuration, or token counting — concerns that belong to other abstractions. Each layer only knows what it needs.

### Separation of Concerns across layers

| Layer       | Responsibility                                    |
|-------------|---------------------------------------------------|
| `frontend`  | User input / output rendering                     |
| `agent/api` | HTTP boundary — deserialise request, serialise response |
| `agent/nodes` | Business logic — state transitions              |
| `core/llm`  | LLM I/O — prompt rendering, structured output    |
| `mcp`       | Database I/O — tool definitions and execution    |
| `postgres`  | Persistence — schema and seed data               |

Each layer depends only on the layer below it, never sideways or upward.

### MCP as an I/O boundary

The MCP server (`backend/mcp/`) is deployed as a separate Docker service and communicates over streamable HTTP. The agent loads tools at startup via `client.py` and treats them as opaque LangChain tools. This means the set of database tools can evolve — or be replaced entirely with a different data source — without touching the agent graph.
