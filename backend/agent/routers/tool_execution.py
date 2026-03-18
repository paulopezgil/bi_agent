from __future__ import annotations

from typing import Literal

from langchain_core.messages import ToolMessage

from backend.agent.config.state import AgentState
from backend.core.logger import get_logger
from backend.utils.parsing import parse_tool_message

logger = get_logger(__name__)


def route_after_tool_execution(state: AgentState) -> Literal["retry", "summarize"]:
    """Route to retry for tool errors; otherwise route to summarize."""
    retry_count = state.get("retry_count", 0)
    messages = state.get("messages", [])

    for message in reversed(messages):
        if isinstance(message, ToolMessage):
            response = parse_tool_message(message)
            if (not response.ok or response.error or response.code) and retry_count < 3:
                logger.info("Conditional edge: execute_tools -> retry")
                return "retry"

            logger.info("Conditional edge: execute_tools -> summarize")
            return "summarize"

    logger.info("No ToolMessage found after execute_tools, routing to summarize")
    return "summarize"
