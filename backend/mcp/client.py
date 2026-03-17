from __future__ import annotations

from contextlib import AsyncExitStack
from typing import Any

from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters
from mcp.client.stdio import stdio_client

from backend.core.logger import get_logger

logger = get_logger(__name__)

_TOOLS_CACHE: list[Any] | None = None
_TOOLS_STACK: AsyncExitStack | None = None


def get_postgres_server_parameters() -> StdioServerParameters:
    """Return stdio server parameters for the Postgres MCP server."""
    server_path = "/app/backend/mcp/server.py"
    logger.info("Using MCP server path: %s", server_path)
    return StdioServerParameters(command="python", args=[server_path])


async def get_db_tools() -> list[Any]:
    """Load and cache MCP tools for the LangGraph agent."""
    global _TOOLS_CACHE
    global _TOOLS_STACK

    if _TOOLS_CACHE is not None:
        return _TOOLS_CACHE

    stack = AsyncExitStack()
    read, write = await stack.enter_async_context(stdio_client(get_postgres_server_parameters()))
    session = await stack.enter_async_context(ClientSession(read, write))

    await session.initialize()
    tools = await load_mcp_tools(session)

    _TOOLS_STACK = stack
    _TOOLS_CACHE = list(tools)
    logger.info("Loaded %d MCP tool(s)", len(_TOOLS_CACHE))
    return _TOOLS_CACHE
