from __future__ import annotations

import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

from backend.core.llm.base import LLMEngine
from backend.core.logger import get_logger

logger = get_logger(__name__)


class LangChainAzureOpenAIEngine(LLMEngine):
    """LangChain + Azure OpenAI implementation of LLMEngine."""

    def __init__(
        self,
        azure_deployment: str | None = None,
        azure_endpoint: str | None = None,
        api_version: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        """
        Args:
            azure_deployment: Azure deployment name. Falls back to ``AZURE_OPENAI_DEPLOYMENT``.
            azure_endpoint:   Azure resource endpoint URL. Falls back to ``AZURE_OPENAI_ENDPOINT``.
            api_version:      Azure OpenAI REST API version. Falls back to
                              ``AZURE_OPENAI_API_VERSION``, then ``2024-02-01``.
            temperature:      Sampling temperature forwarded to ``AzureChatOpenAI``.
        """
        self._azure_deployment = azure_deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self._azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self._api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
        self._temperature = temperature

    async def generate(
        self,
        output_schema: type[BaseModel],
        prompt_template: str,
        inputs: dict,
    ) -> dict:
        """Render *prompt_template*, call AzureChatOpenAI with structured output, dump to dict.

        Args:
            output_schema:   Pydantic model class used to bind structured output.
            prompt_template: Prompt string with ``{key}`` placeholders.
            inputs:          Mapping of placeholder names to values.

        Returns:
            ``output_schema`` instance serialised via ``model_dump()``.

        Raises:
            ValueError: If the LLM response cannot be parsed into ``output_schema``.
        """
        logger.info(
            "LangChainAzureOpenAIEngine.generate | deployment=%s schema=%s",
            self._azure_deployment,
            output_schema.__name__,
        )

        llm = AzureChatOpenAI(
            azure_deployment=self._azure_deployment,
            azure_endpoint=self._azure_endpoint,
            api_version=self._api_version,
            temperature=self._temperature,
        )
        structured_llm = llm.with_structured_output(output_schema)
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | structured_llm

        result = await chain.ainvoke(inputs)

        if not isinstance(result, BaseModel):
            raise ValueError(
                f"Expected a Pydantic model from structured output, got {type(result)}"
            )

        return result.model_dump()
