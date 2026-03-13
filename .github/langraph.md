# LangGraph Orchestration Context

## Current Implementation Location
- `backend/agent/app/graph.py`

## State Definition (Current)
`AgentState` contains:
- `question`: user natural language request
- `sql`: SQL currently being tested
- `retries`: retry counter (max 3)
- `error`: latest execution error
- `rows`: query results
- `answer`: final user-facing response

## Current Graph Flow
1. `planner`: generates SQL from question.
2. `execute_query`: calls MCP `/tools/execute_readonly_query`.
3. `error_handler`: increments retries on failure.
4. `format_answer`: formats final message.
5. conditional edge `should_retry`: loops while `error` exists and retries < 3.

## Completion Criteria
- Retry loop must stop at 3 attempts.
- Error text must be preserved for debugging and user feedback.
- Success path returns `rows`, `sql`, and `answer`.

## Next Improvements
1. Introduce schema-introspection step using MCP list/describe tools.
2. Use LLM prompt templates for SQL generation and error correction.
3. Add deterministic tests for retry and max-retry termination.
