# MCP Server Specification (PostgreSQL)

## Protocol
- Use the `mcp` Python SDK to create a Standard Input/Output server.
- The server must run in a separate process or container from the LangGraph agent.
- Current container target: `docker/mcp/Dockerfile` running `python -m src.mcp_server.server`.

## Tools to Implement
1. **`list_tables`**: 
   - Input: None
   - Output: List of table names in the 'public' schema.
2. **`describe_table`**:
   - Input: `table_name` (str)
   - Output: Column names, types, and foreign key relationships.
3. **`execute_readonly_query`**:
   - Input: `query` (str)
   - Logic: Must wrap the execution in a transaction that is immediately rolled back or use a Read-Only user role to prevent `INSERT/UPDATE/DELETE`.
   - Output: JSON formatted rows or clear error messages.

## Error Handling Requirements
- Catch `psycopg2.Error` subclasses and return structured error text without crashing the server process.
- Reject non-read-only statements (`INSERT`, `UPDATE`, `DELETE`, `ALTER`, `DROP`, etc.) before execution.
- Include database error code and message in tool output when available.
- Always close cursor/connection resources safely.

## Implementation Checklist
1. Add DB connection helper using env vars (`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`).
2. Implement each tool with typed inputs/outputs.
3. Normalize output to JSON-serializable dictionaries/lists.
4. Add unit tests for success, syntax error, permission error, and blocked write-query behavior.