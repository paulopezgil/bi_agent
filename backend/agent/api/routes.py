from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request
from langchain_core.messages import AIMessage, ToolMessage

from backend.agent.api.schemas import ChatRequest, ChatResponse
from backend.core.logger import get_logger
from backend.utils.parsing import parse_tool_message

router = APIRouter()
logger = get_logger(__name__)


def _extract_response(state: dict) -> ChatResponse:
    """Pull answer, sql, retries, and rows out of a completed AgentState."""
    messages = state.get("messages", [])
    retry_count = state.get("retry_count", 0)

    # Answer: content of the last AIMessage without tool calls
    answer = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not msg.tool_calls:
            content = msg.content
            answer = content if isinstance(content, str) else str(content)
            break

    # SQL: args of the last AIMessage that had tool calls
    sql = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            raw_args = msg.tool_calls[0].get("args", {})
            if isinstance(raw_args, dict):
                sql = raw_args.get("query", raw_args.get("sql", json.dumps(raw_args)))
            else:
                sql = str(raw_args)
            break

    # Rows: data from the last successful ToolMessage
    rows = []
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            response = parse_tool_message(msg)
            if response.ok and response.data is not None:
                raw_rows = response.data.get("rows", [])
                if isinstance(raw_rows, list):
                    rows = raw_rows
            break

    return ChatResponse(answer=answer, sql=sql, retries=retry_count, rows=rows, error="")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    graph = request.app.state.graph
    if graph is None:
        raise HTTPException(status_code=503, detail="Agent graph not initialised")

    logger.info("POST /chat message=%r", body.message[:120])

    try:
        initial_state = {
            "messages": [{"role": "user", "content": body.message}],
            "is_safe": True,
            "retry_count": 0,
        }
        final_state = await graph.ainvoke(initial_state)
        return _extract_response(final_state)
    except Exception as exc:
        logger.exception("Graph invocation failed: %s", exc)
        return ChatResponse(answer="", sql="", retries=0, rows=[], error=str(exc))
