"""Tests for the query_database node.

Input:  AgentState with messages and retry_count.
Output: A list containing the model's response message.
        If the retry budget is exhausted and the last tool call failed,
        the node returns a fallback AIMessage without calling the engine.

The LLM call is mocked — no MCP patching needed since tools are injected.
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from backend.agent.nodes.query_database import make_query_database_node


def _mock_engine(response: AIMessage) -> MagicMock:
    engine = MagicMock()
    engine.generate_with_tools = AsyncMock(return_value=response)
    return engine


def _failed_tool_msg() -> ToolMessage:
    return ToolMessage(
        content=json.dumps({"ok": False, "error": "relation does not exist", "code": "42P01"}),
        tool_call_id="call_1",
    )


def _success_tool_msg() -> ToolMessage:
    return ToolMessage(
        content=json.dumps({"ok": True, "rows": [{"count": 5}], "row_count": 1}),
        tool_call_id="call_1",
    )


# ── Normal flow ───────────────────────────────────────────────────────────────

async def test_returns_engine_response_as_message() -> None:
    ai_response = AIMessage(content="There are 42 customers.")
    engine = _mock_engine(ai_response)
    query_database = make_query_database_node([], engine)
    state = {"messages": [HumanMessage(content="How many customers?")], "retry_count": 0, "is_safe": True}
    result = await query_database(state)
    assert result["messages"][0] is ai_response


async def test_response_containing_tool_calls_is_returned_as_is() -> None:
    ai_response = AIMessage(content="", tool_calls=[{"name": "execute_readonly_query", "args": {"query": "SELECT COUNT(*) FROM customers"}, "id": "call_1"}])
    engine = _mock_engine(ai_response)
    query_database = make_query_database_node([], engine)
    state = {"messages": [HumanMessage(content="Count customers")], "retry_count": 0, "is_safe": True}
    result = await query_database(state)
    assert isinstance(result["messages"][0], AIMessage)
    assert result["messages"][0].tool_calls


# ── Retry budget exhausted ────────────────────────────────────────────────────

async def test_retry_budget_exhausted_returns_fallback_without_calling_engine() -> None:
    engine = MagicMock()
    engine.generate_with_tools = AsyncMock()
    query_database = make_query_database_node([], engine)
    state = {
        "messages": [HumanMessage(content="Count customers"), _failed_tool_msg()],
        "retry_count": 3,
        "is_safe": True,
    }
    result = await query_database(state)
    engine.generate_with_tools.assert_not_called()
    assert isinstance(result["messages"][0], AIMessage)
    assert "3 retry" in result["messages"][0].content


async def test_retry_budget_exhausted_but_last_tool_succeeded_still_calls_engine() -> None:
    ai_response = AIMessage(content="Done.")
    engine = _mock_engine(ai_response)
    query_database = make_query_database_node([], engine)
    state = {
        "messages": [HumanMessage(content="Count customers"), _success_tool_msg()],
        "retry_count": 3,
        "is_safe": True,
    }
    result = await query_database(state)
    engine.generate_with_tools.assert_called_once()
    assert result["messages"][0] is ai_response
