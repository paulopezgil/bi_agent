from __future__ import annotations

import os

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from backend.core.llm.base import LLMEngine
from backend.core.logger import get_logger

logger = get_logger(__name__)


class LangChainOpenAIEngine(LLMEngine):
    """LangChain + OpenAI implementation of ``LLMEngine``."""

    def __init__(self, model: str | None = None, temperature: float = 0.0) -> None:
        """
        Args:
            model:       OpenAI model identifier. Falls back to the
                         ``OPENAI_MODEL`` environment variable, then ``gpt-4o``.
            temperature: Sampling temperature forwarded to ``ChatOpenAI``.
        """
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self._temperature = temperature
        super().__init__()

    def _build_llm(self) -> BaseChatModel:
        logger.info("Initialising ChatOpenAI | model=%s", self._model)
        return ChatOpenAI(model=self._model, temperature=self._temperature)
