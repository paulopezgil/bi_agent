"""Tests for the handle_tool_result node.

Input:  AgentState whose messages list may contain a ToolMessage as the last
        relevant item.  The node inspects the ToolMessage payload to decide
        whether a Postgres error occurred.
Output: If an error is detected and retry_count < 3  → incremented retry_count
        + a SystemMessage asking the model to fix its SQL.
        Otherwise                                    → retry_count unchanged,
        no new messages.
"""
from __future__ import annotations

import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from backend.agent.nodes.handle_tool_result import handle_tool_result


def _tool_msg(payload: dict) -> ToolMessage:
    return ToolMessage(content=json.dumps(payload), tool_call_id="call_1")


# ── No ToolMessage present ────────────────────────────────────────────────────

async def test_no_tool_message_returns_retry_count_unchanged() -> None:
    state = {"messages": [HumanMessage(content="hi")], "retry_count": 1, "is_safe": True}
    result = await handle_tool_result(state)
    assert result["retry_count"] == 1
    assert "messages" not in result


async def test_empty_messages_returns_retry_count_unchanged() -> None:
    state = {"messages": [], "retry_count": 0, "is_safe": True}
    result = await handle_tool_result(state)
    assert result["retry_count"] == 0


# ── Error payloads trigger a retry ───────────────────────────────────────────

async def test_ok_false_increments_retry_count() -> None:
    state = {
        "messages": [_tool_msg({"ok": False, "error": "relation does not exist", "code": "42P01"})],
        "retry_count": 0,
        "is_safe": True,
    }
    result = await handle_tool_result(state)
    assert result["retry_count"] == 1


async def test_ok_false_appends_system_message() -> None:
    state = {
        "messages": [_tool_msg({"ok": False, "error": "relation does not exist", "code": "42P01"})],
        "retry_count": 0,
        "is_safe": True,
    }
    result = await handle_tool_result(state)
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], SystemMessage)


async def test_syntax_error_in_raw_triggers_retry() -> None:
    state = {
        "messages": [_tool_msg({"ok": False, "raw": "ERROR: syntax error at or near SELECT"})],
        "retry_count": 0,
        "is_safe": True,
    }
    result = await handle_tool_result(state)
    assert result["retry_count"] == 1


async def test_system_message_references_retry_number() -> None:
    state = {
        "messages": [_tool_msg({"ok": False, "code": "42P01"})],
        "retry_count": 1,
        "is_safe": True,
    }
    result = await handle_tool_result(state)
    assert "2/3" in result["messages"][0].content


# ── Successful payload does not trigger a retry ───────────────────────────────

async def test_successful_tool_result_no_retry() -> None:
    state = {
        "messages": [_tool_msg({"ok": True, "rows": [{"total": 42}], "row_count": 1})],
        "retry_count": 0,
        "is_safe": True,
    }
    result = await handle_tool_result(state)
    assert result["retry_count"] == 0
    assert "messages" not in result


# ── Retry budget exhausted ────────────────────────────────────────────────────

async def test_retry_budget_exhausted_does_not_increment() -> None:
    state = {
        "messages": [_tool_msg({"ok": False, "code": "42P01"})],
        "retry_count": 3,
        "is_safe": True,
    }
    result = await handle_tool_result(state)
    assert result["retry_count"] == 3
    assert "messages" not in result


# ── Node scans the full message list for the last ToolMessage ─────────────────

async def test_uses_last_tool_message_in_list() -> None:
    state = {
        "messages": [
            _tool_msg({"ok": False, "code": "42P01"}),        # earlier failure
            AIMessage(content="Retrying..."),
            _tool_msg({"ok": True, "rows": [], "row_count": 0}),  # latest success
        ],
        "retry_count": 1,
        "is_safe": True,
    }
    result = await handle_tool_result(state)
    # Latest ToolMessage is a success → no retry
    assert result["retry_count"] == 1
    assert "messages" not in result
