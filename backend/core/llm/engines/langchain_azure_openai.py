from __future__ import annotations

import os

from langchain_core.language_models import BaseChatModel
from langchain_openai import AzureChatOpenAI

from backend.core.llm.base import LLMEngine
from backend.core.logger import get_logger

logger = get_logger(__name__)


class LangChainAzureOpenAIEngine(LLMEngine):
    """LangChain + Azure OpenAI implementation of ``LLMEngine``."""

    def __init__(
        self,
        model: str | None = None,
        azure_endpoint: str | None = None,
        api_version: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        """
        Args:
            model:          Azure deployment name. Falls back to
                            ``AZURE_OPENAI_DEPLOYMENT``. Named ``model`` so
                            the factory can use a single keyword argument
                            across all engines.
            azure_endpoint: Azure resource endpoint URL. Falls back to
                            ``AZURE_OPENAI_ENDPOINT``.
            api_version:    Azure OpenAI REST API version. Falls back to
                            ``AZURE_OPENAI_API_VERSION``, then
                            ``2024-08-01-preview``.
            temperature:    Sampling temperature forwarded to
                            ``AzureChatOpenAI``.
        """
        self._model = model or os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self._azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self._api_version = api_version or os.getenv(
            "AZURE_OPENAI_API_VERSION", "2024-08-01-preview"
        )
        self._temperature = temperature
        super().__init__()

    def _build_llm(self) -> BaseChatModel:
        logger.info("Initialising AzureChatOpenAI | deployment=%s", self._model)
        return AzureChatOpenAI(
            azure_deployment=self._model,
            azure_endpoint=self._azure_endpoint,
            api_version=self._api_version,
            temperature=self._temperature,
        )
