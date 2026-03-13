# LangGraph Orchestration Context

## State Definition
The `AgentState` is a `TypedDict` containing:
- `messages`: Annotated[list, add_messages] (Chat history)
- `schema_context`: String containing relevant DB schema.
- `retry_count`: Integer to track SQL fix attempts (Max 3).
- `pending_query`: The raw SQL string currently being tested.

Implementation note:
- Treat state as immutable in node handlers; always return a new state object.

## The Graph Flow
1. **Node: `planner`**: Analyzes user intent and decides if DB access is needed.
2. **Node: `get_schema`**: Calls MCP tool to fetch table/column definitions.
3. **Node: `sql_generator`**: Writes the SQL query based on schema.
4. **Node: `execute_query`**: Calls the MCP `execute_readonly_query` tool.
5. **Node: `error_handler`**: If `execute_query` returns a Database Error, this node increments `retry_count` and sends the error back to `sql_generator`.
6. **Edge: `should_continue`**: Conditional mapping to decide if the loop ends or retries.

## Completion Criteria
- Retry loop stops at `retry_count >= 3` with a user-facing failure explanation.
- On SQL error, the next `sql_generator` prompt includes the exact DB error string.
- Successful execution appends tool results to `messages` and resets `pending_query`.