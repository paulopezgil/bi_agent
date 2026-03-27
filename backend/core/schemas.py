from __future__ import annotations

from pydantic import BaseModel


class ToolResponse(BaseModel):
    ok: bool
    data: dict | None = None
    error: str | None = None
    code: str | None = None
