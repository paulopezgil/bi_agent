from __future__ import annotations

import psycopg2

from backend.core.logger import get_logger
from backend.core.schemas import ToolResponse

logger = get_logger(__name__)


def handle_tool_exception(exc: Exception) -> ToolResponse:
    """Normalize tool exceptions into a consistent ToolResponse payload."""
    logger.exception("MCP tool execution failed")

    if isinstance(exc, psycopg2.Error):
        return ToolResponse(ok=False, error=str(exc), code=exc.pgcode)

    return ToolResponse(ok=False, error=str(exc))