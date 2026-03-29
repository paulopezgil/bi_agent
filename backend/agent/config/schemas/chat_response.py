from __future__ import annotations

from pydantic import BaseModel


class ChatResponse(BaseModel):
    answer: str
    sql: str
    retries: int
    rows: list
    error: str
