"""Graph-level happy path tests.

Verifies that when the tool call succeeds on the first attempt the graph
reaches the end state without any retries.
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from backend.agent.graph import compile_graph
from backend.agent.nodes.guardrail import GuardrailDecision


def _fake_tools(responses: list[str]) -> list:
    it = iter(responses)

    @tool
    def execute_readonly_query(query: str) -> str:
        """Execute a read-only SQL query against the database."""
        return next(it)

    return [execute_readonly_query]


def _mock_engine(tool_call_responses: list[AIMessage]) -> MagicMock:
    engine = MagicMock()
    engine.generate_structured = AsyncMock(
        return_value=GuardrailDecision(is_safe=True, reason="safe")
    )
    engine.generate_with_tools = AsyncMock(side_effect=tool_call_responses)
    return engine


async def test_graph_succeeds_without_retry() -> None:
    """Tool succeeds on first call; retry_count stays at 0."""
    fake_tools = _fake_tools([
        json.dumps({"ok": True, "rows": [{"total_count": 42}], "row_count": 1}),
    ])
    engine = _mock_engine([
        AIMessage(content="", tool_calls=[{
            "name": "execute_readonly_query",
            "args": {"query": "SELECT COUNT(*) FROM customers"},
            "id": "call_1",
            "type": "tool_call",
        }]),
        AIMessage(content="There are 42 customers."),
    ])

    with (
        patch("backend.agent.graph.compile.get_db_tools", new_callable=AsyncMock, return_value=fake_tools),
        patch("backend.agent.graph.compile.EngineFactory.create_default", return_value=engine),
    ):
        graph = await compile_graph()
        state = await graph.ainvoke({"messages": [HumanMessage(content="How many customers?")]})

    assert state["retry_count"] == 0
    assert "42 customers" in state["messages"][-1].content
