from __future__ import annotations

import os
from contextlib import AsyncExitStack
from typing import Any

from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from backend.core.logger import get_logger

logger = get_logger(__name__)

_TOOLS_CACHE: list[Any] | None = None
_TOOLS_STACK: AsyncExitStack | None = None


def get_mcp_url() -> str:
    return os.getenv("MCP_BASE_URL", "http://mcp:8001/mcp")


async def get_db_tools() -> list[Any]:
    """Load and cache MCP tools for the LangGraph agent."""
    global _TOOLS_CACHE
    global _TOOLS_STACK

    if _TOOLS_CACHE is not None:
        return _TOOLS_CACHE

    url = get_mcp_url()
    logger.info("Connecting to MCP server at %s", url)

    stack = AsyncExitStack()
    read, write, _ = await stack.enter_async_context(streamablehttp_client(url))
    session = await stack.enter_async_context(ClientSession(read, write))

    await session.initialize()
    tools = await load_mcp_tools(session)

    _TOOLS_STACK = stack
    _TOOLS_CACHE = list(tools)
    logger.info("Loaded %d MCP tool(s)", len(_TOOLS_CACHE))
    return _TOOLS_CACHE
