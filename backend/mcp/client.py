from __future__ import annotations

from mcp.client.stdio import StdioServerParameters

from backend.core.logger import get_logger

logger = get_logger(__name__)


def get_postgres_server_parameters() -> StdioServerParameters:
    """Return stdio server parameters for the Postgres MCP server."""
    server_path = "/app/backend/mcp/server.py"
    logger.info("Using MCP server path: %s", server_path)
    return StdioServerParameters(command="python", args=[server_path])
