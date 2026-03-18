from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ToolResponse(BaseModel):
    ok: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    code: str | None = None
