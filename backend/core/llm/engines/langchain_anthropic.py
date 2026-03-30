from __future__ import annotations

import os

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel

from backend.core.llm.base import LLMEngine
from backend.core.logger import get_logger

logger = get_logger(__name__)


class LangChainAnthropicEngine(LLMEngine):
    """LangChain + Anthropic implementation of ``LLMEngine``."""

    def __init__(self, model: str | None = None, temperature: float = 0.0) -> None:
        """
        Args:
            model:       Anthropic model identifier. Falls back to the
                         ``ANTHROPIC_MODEL`` environment variable, then
                         ``claude-sonnet-4-6``.
            temperature: Sampling temperature forwarded to ``ChatAnthropic``.
        """
        self._model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        self._temperature = temperature
        super().__init__()

    def _build_llm(self) -> BaseChatModel:
        logger.info("Initialising ChatAnthropic | model=%s", self._model)
        return ChatAnthropic(model=self._model, temperature=self._temperature)
