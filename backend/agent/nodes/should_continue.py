from __future__ import annotations
from typing import Literal
from langchain_core.messages import AIMessage

from backend.agent.state import AgentState
from backend.core.logger import get_logger


logger = get_logger(__name__)

def should_continue(state: AgentState) -> Literal["call_tool", "end"]:
    """Route to tool execution when the model emits tool calls."""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        logger.info("Conditional edge: call_model -> call_tool")
        return "call_tool"

    logger.info("Conditional edge: call_model -> END")
    return "end"