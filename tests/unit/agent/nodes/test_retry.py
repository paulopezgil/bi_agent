"""Tests for the retry node.

Input:  AgentState with retry_count and messages.
Output: incremented retry_count + a SystemMessage instructing the model to fix its SQL.
"""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from backend.agent.nodes.retry import retry


async def test_increments_retry_count() -> None:
    state = {"messages": [HumanMessage(content="Count customers")], "retry_count": 0, "is_safe": True}
    result = await retry(state)
    assert result["retry_count"] == 1


async def test_increments_from_nonzero_count() -> None:
    state = {"messages": [], "retry_count": 2, "is_safe": True}
    result = await retry(state)
    assert result["retry_count"] == 3


async def test_appends_one_system_message() -> None:
    state = {"messages": [], "retry_count": 0, "is_safe": True}
    result = await retry(state)
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], SystemMessage)


async def test_system_message_references_retry_number() -> None:
    state = {"messages": [], "retry_count": 1, "is_safe": True}
    result = await retry(state)
    assert "2/3" in result["messages"][0].content