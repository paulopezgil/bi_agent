# Project Architecture & Rules

## Overview
A production-grade AI Analyst Agent built with LangGraph and MCP. The system allows users to query a PostgreSQL database using natural language, with self-healing SQL generation.

## Current Build State
- Container topology exists and is orchestrated by root `docker-compose.yml`.
- Services: `agent`, `mcp`, `postgres`.
- Database bootstrap currently comes from `docker/postgres/init.sql`.
- `src/main.py` and `src/mcp_server/server.py` are placeholders and must be implemented.

## Directory Structure
- `src/agent/`: Core LangGraph orchestration logic.
- `src/mcp_server/`: MCP server implementation for DB tools.
- `src/shared/`: Shared Pydantic models and utility functions.
- `tests/`: Pytest suite for nodes and tools.
- `docker/agent/`: Docker build context for agent runtime.
- `docker/mcp/`: Docker build context for MCP server runtime.
- `docker/postgres/init.sql`: local development schema + seed data.
- `docker-compose.yml`: service orchestration for local stack.

## Key Principles
1. **Strict Typing**: Use Python type hints and Pydantic models for all data structures.
2. **Separation of Concerns**: The Agent (Graph) must not have DB credentials. It only interacts with tools via the MCP client.
3. **Immutability**: Treat the AgentState as immutable; always return a new state in nodes.
4. **Dependency Management**: Use `uv` for lightning-fast environment setup and locking.

## Immediate Priorities
1. Replace placeholder `src/mcp_server/server.py` with full MCP tool server.
2. Implement LangGraph in `src/agent/graph.py` with immutable state returns.
3. Replace placeholder `src/main.py` with REPL + MCP client wiring.
4. Add tests for MCP tool error handling and graph self-correction loop.