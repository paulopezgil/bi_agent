from __future__ import annotations

import json

from langchain_core.messages import SystemMessage, ToolMessage

from backend.agent.config.state import AgentState
from backend.core.logger import get_logger

logger = get_logger(__name__)


def _normalize_tool_payload(content: str | dict) -> dict:
    if isinstance(content, dict):
        return content

    if isinstance(content, str):
        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {"raw": content}

    return {"raw": str(content)}


def _is_postgres_error(payload: dict) -> bool:
    raw = str(payload.get("raw", "")).lower()
    err = str(payload.get("error", "")).lower()
    code = payload.get("code")

    return bool(
        code
        or "postgres" in raw
        or "postgres" in err
        or "relation does not exist" in raw
        or "relation does not exist" in err
        or "syntax error" in raw
        or "syntax error" in err
        or payload.get("ok") is False
    )


async def handle_tool_result(state: AgentState) -> AgentState:
    """Increment retry count and steer model correction when DB errors are detected."""
    logger.info("Node transition: handle_tool_result")

    retry_count = state.get("retry_count", 0)
    messages = state.get("messages", [])

    last_tool = None
    for message in reversed(messages):
        if isinstance(message, ToolMessage):
            last_tool = message
            break

    if last_tool is None:
        return {"retry_count": retry_count}

    payload = _normalize_tool_payload(last_tool.content)
    if _is_postgres_error(payload) and retry_count < 3:
        updated_retry_count = retry_count + 1
        logger.info("Detected DB error. Triggering retry %d/3", updated_retry_count)
        return {
            "retry_count": updated_retry_count,
            "messages": [
                SystemMessage(
                    content=(
                        "The previous SQL execution failed with a Postgres Error. "
                        "Correct the SQL and call the appropriate tool again. "
                        f"Retry attempt: {updated_retry_count}/3."
                    )
                )
            ],
        }

    return {"retry_count": retry_count}
