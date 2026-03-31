"""Tests for the guardrail node.

Input:  AgentState with at least one message whose content will be classified.
Output: is_safe (bool) + retry_count passed through.

The LLM call is mocked — these tests verify the node's wiring and branching
logic, not the classifier's quality.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from langchain_core.messages import AIMessage, HumanMessage

from backend.agent.nodes.guardrail import GuardrailDecision, make_guardrail_node


def _mock_engine(is_safe: bool, reason: str = "ok") -> MagicMock:
    engine = MagicMock()
    engine.generate_structured = AsyncMock(
        return_value=GuardrailDecision(is_safe=is_safe, reason=reason)
    )
    return engine


# ── Normal classification ─────────────────────────────────────────────────────

async def test_safe_request_sets_is_safe_true() -> None:
    guardrail = make_guardrail_node(_mock_engine(True))
    state = {"messages": [HumanMessage(content="How many customers do we have?")], "retry_count": 0, "is_safe": True}
    result = await guardrail(state)
    assert result["is_safe"] is True


async def test_unsafe_request_sets_is_safe_false() -> None:
    guardrail = make_guardrail_node(_mock_engine(False, "injection attempt"))
    state = {"messages": [HumanMessage(content="DROP TABLE users;")], "retry_count": 0, "is_safe": True}
    result = await guardrail(state)
    assert result["is_safe"] is False


async def test_preserves_retry_count() -> None:
    guardrail = make_guardrail_node(_mock_engine(True))
    state = {"messages": [HumanMessage(content="Show revenue")], "retry_count": 2, "is_safe": True}
    result = await guardrail(state)
    assert result["retry_count"] == 2


# ── Short-circuit on empty input (no LLM call) ───────────────────────────────

async def test_empty_message_content_marks_unsafe_without_calling_engine() -> None:
    engine = MagicMock()
    engine.generate_structured = AsyncMock()
    guardrail = make_guardrail_node(engine)
    state = {"messages": [HumanMessage(content="")], "retry_count": 0, "is_safe": True}
    result = await guardrail(state)
    assert result["is_safe"] is False
    engine.generate_structured.assert_not_called()


async def test_no_messages_marks_unsafe_without_calling_engine() -> None:
    engine = MagicMock()
    engine.generate_structured = AsyncMock()
    guardrail = make_guardrail_node(engine)
    state = {"messages": [], "retry_count": 0, "is_safe": True}
    result = await guardrail(state)
    assert result["is_safe"] is False
    engine.generate_structured.assert_not_called()


# ── Reads content from the last message ───────────────────────────────────────

async def test_classifies_last_message_in_list() -> None:
    engine = _mock_engine(True)
    guardrail = make_guardrail_node(engine)
    state = {
        "messages": [
            HumanMessage(content="first message"),
            AIMessage(content="agent reply"),
            HumanMessage(content="second user question"),
        ],
        "retry_count": 0,
        "is_safe": True,
    }
    await guardrail(state)
    messages_arg = engine.generate_structured.call_args[0][1]
    assert any("second user question" in str(m.content) for m in messages_arg)
