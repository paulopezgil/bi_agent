from __future__ import annotations

import os

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from backend.core.llm.base import LLMEngine
from backend.core.logger import get_logger

logger = get_logger(__name__)


class LangChainAnthropicEngine(LLMEngine):
    """LangChain + Anthropic implementation of LLMEngine."""

    def __init__(self, model: str | None = None, temperature: float = 0.0) -> None:
        """
        Args:
            model:       Anthropic model identifier.  Falls back to the
                         ``ANTHROPIC_MODEL`` environment variable, then
                         ``claude-sonnet-4-6``.
            temperature: Sampling temperature forwarded to ``ChatAnthropic``.
        """
        self._model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        self._temperature = temperature

    async def generate(
        self,
        output_schema: type[BaseModel],
        prompt_template: str,
        inputs: dict,
    ) -> dict:
        """Render *prompt_template*, call ChatAnthropic with structured output, dump to dict.

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
            "LangChainAnthropicEngine.generate | model=%s schema=%s",
            self._model,
            output_schema.__name__,
        )

        llm = ChatAnthropic(model=self._model, temperature=self._temperature)
        structured_llm = llm.with_structured_output(output_schema)
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | structured_llm

        result = await chain.ainvoke(inputs)

        if not isinstance(result, BaseModel):
            raise ValueError(
                f"Expected a Pydantic model from structured output, got {type(result)}"
            )

        return result.model_dump()
