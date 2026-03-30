"""Tests for the security_warning node.

Input:  Any AgentState (the node ignores it entirely).
Output: A single AIMessage with a fixed security warning text.
"""
from __future__ import annotations

from langchain_core.messages import AIMessage

from backend.agent.nodes.security_warning import security_warning


async def test_returns_single_ai_message() -> None:
    state = {"messages": [], "retry_count": 0, "is_safe": False}
    result = await security_warning(state)
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)


async def test_message_contains_security_warning() -> None:
    state = {"messages": [], "retry_count": 0, "is_safe": False}
    result = await security_warning(state)
    assert "Security Warning" in result["messages"][0].content


async def test_ignores_existing_messages_in_state() -> None:
    state = {"messages": [AIMessage(content="previous")], "retry_count": 0, "is_safe": False}
    result = await security_warning(state)
    # Node only returns the warning — it does not echo back existing messages
    assert len(result["messages"]) == 1
