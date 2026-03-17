from __future__ import annotations

import os

from langchain_openai import ChatOpenAI

from backend.core.logger import get_logger

logger = get_logger(__name__)


def get_chat_openai(model: str | None = None, temperature: float = 0.0) -> ChatOpenAI:
    """Create a shared ChatOpenAI client with environment defaults."""
    resolved_model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
    logger.info("Creating ChatOpenAI client with model=%s", resolved_model)
    return ChatOpenAI(model=resolved_model, temperature=temperature)
