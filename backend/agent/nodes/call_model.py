from __future__ import annotations

import json

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.messages import ToolMessage

from backend.agent.state import AgentState

from backend.agent.prompts import SYSTEM_PROMPT
from backend.core.logger import get_logger
from backend.core.openai_client import get_chat_openai
from backend.mcp.client import get_db_tools


logger = get_logger(__name__)


def _is_tool_error_message(message: ToolMessage) -> bool:
    content = message.content
    if isinstance(content, dict):
        payload = content
    elif isinstance(content, str):
        try:
            parsed = json.loads(content)
            payload = parsed if isinstance(parsed, dict) else {"raw": content}
        except json.JSONDecodeError:
            payload = {"raw": content}
    else:
        payload = {"raw": str(content)}

    raw = str(payload.get("raw", "")).lower()
    err = str(payload.get("error", "")).lower()
    return payload.get("ok") is False or bool(payload.get("code")) or "error" in raw or "error" in err

async def call_model(state: AgentState) -> AgentState:
    """Invoke the LLM with tools bound for plan-and-execute behavior."""
    logger.info("Node transition: call_model")

    if state.get("is_safe") is False:
        logger.warning("Security guardrail prevented model/tool execution")
        return {
            "messages": [
                AIMessage(
                    content=(
                        "Security Warning: The request appears unsafe and may contain "
                        "destructive or injection-like SQL instructions."
                    )
                )
            ]
        }

    retry_count = state.get("retry_count", 0)
    last_message = state.get("messages", [])[-1] if state.get("messages") else None
    if (
        retry_count >= 3
        and isinstance(last_message, ToolMessage)
        and _is_tool_error_message(last_message)
    ):
        logger.warning("Retry budget exhausted after database errors")
        return {
            "messages": [
                AIMessage(
                    content=(
                        "I could not produce a valid SQL query after 3 retry attempts. "
                        "Please rephrase your question or provide more schema context."
                    )
                )
            ]
        }

    tools = await get_db_tools()
    llm = get_chat_openai(temperature=0)
    model_with_tools = llm.bind_tools(tools)

    response = await model_with_tools.ainvoke(
        [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    )

    if isinstance(response, AIMessage) and response.tool_calls:
        logger.info("call_model requested %d tool call(s)", len(response.tool_calls))
    else:
        logger.info("call_model produced final response")

    return {"messages": [response]}