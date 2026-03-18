from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import ToolMessage
from pydantic import ValidationError

from backend.core.schemas import ToolResponse


def parse_tool_message(message: ToolMessage) -> ToolResponse:
    content = message.content
    payload: dict[str, Any]

    if isinstance(content, dict):
        payload = content
    elif isinstance(content, str):
        try:
            parsed = json.loads(content)
            payload = (
                parsed if isinstance(parsed, dict)
                else {"ok": False, "error": content}
            )
        except json.JSONDecodeError:
            payload = {"ok": False, "error": content}
    else:
        payload = {"ok": False, "error": str(content)}

    try:
        return ToolResponse.model_validate(payload)
    except ValidationError:
        return ToolResponse(ok=False, error=str(payload))
