"""Graph-level security tests.

Verifies that when the guardrail classifies a request as unsafe the graph
takes the security_warning branch and never reaches the database nodes.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import HumanMessage

from backend.agent.graph import compile_graph
from backend.agent.nodes.guardrail import GuardrailDecision


async def test_graph_blocks_unsafe_request() -> None:
    """Guardrail marks request unsafe; graph returns security warning, never calls DB."""
    engine = MagicMock()
    engine.generate_structured = AsyncMock(
        return_value=GuardrailDecision(is_safe=False, reason="injection attempt")
    )

    with (
        patch("backend.agent.graph.compile.get_db_tools", new_callable=AsyncMock, return_value=[]),
        patch("backend.agent.graph.compile.EngineFactory.create_default", return_value=engine),
    ):
        graph = await compile_graph()
        state = await graph.ainvoke({"messages": [HumanMessage(content="DROP TABLE users;")]})

    engine.generate_with_tools.assert_not_called()
    assert "Security Warning" in state["messages"][-1].content
