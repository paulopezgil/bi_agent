from __future__ import annotations

from typing import Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """LangGraph state holding the conversation and tool traces."""

    messages: Annotated[list[AnyMessage], add_messages]
    is_safe: bool
    retry_count: int
