from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from backend.core.logger import get_logger
from backend.core.schemas import ToolResponse
from backend.mcp.tools.describe_table import run_describe_table
from backend.mcp.tools.execute_readonly_query import run_execute_readonly_query
from backend.mcp.tools.list_tables import run_list_tables

logger = get_logger(__name__)
mcp = FastMCP(
    name="Postgres-Assistant",
    host="0.0.0.0",
    port=8001,
)


@mcp.tool()
def list_tables() -> ToolResponse:
    """Return all tables in the public schema."""
    return run_list_tables()


@mcp.tool()
def describe_table(table_name: str) -> ToolResponse:
    """Describe a table's columns and foreign keys."""
    return run_describe_table(table_name)


@mcp.tool()
def execute_readonly_query(query: str) -> ToolResponse:
    """Execute SQL query. Validation is delegated upstream."""
    return run_execute_readonly_query(query)


if __name__ == "__main__":
    logger.info("Starting Postgres-Assistant MCP server on 0.0.0.0:8001")
    mcp.run(transport="streamable-http")
