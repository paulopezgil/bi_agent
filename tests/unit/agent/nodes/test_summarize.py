"""Tests for the summarize node.

Input:  AgentState with retry_count (and any messages).
Output: retry_count passed through unchanged. No new messages are added.
        This node is a pass-through that makes the successful-tool routing
        explicit in the graph.
"""
from __future__ import annotations

from langchain_core.messages import AIMessage

from backend.agent.nodes.summarize import summarize


async def test_passes_through_retry_count() -> None:
    state = {"messages": [], "retry_count": 2, "is_safe": True}
    result = await summarize(state)
    assert result["retry_count"] == 2


async def test_defaults_retry_count_to_zero_when_missing() -> None:
    state = {"messages": [], "is_safe": True}
    result = await summarize(state)
    assert result["retry_count"] == 0


async def test_does_not_add_messages() -> None:
    state = {"messages": [AIMessage(content="some result")], "retry_count": 1, "is_safe": True}
    result = await summarize(state)
    assert "messages" not in result
