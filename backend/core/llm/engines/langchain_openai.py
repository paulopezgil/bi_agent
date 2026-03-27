from __future__ import annotations

import os
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from backend.core.llm.base import LLMEngine
from backend.core.logger import get_logger

logger = get_logger(__name__)


class LangChainOpenAIEngine(LLMEngine):
    """LangChain + OpenAI implementation of LLMEngine."""

    def __init__(self, model: str | None = None, temperature: float = 0.0) -> None:
        """
        Args:
            model:       OpenAI model identifier.  Falls back to the
                         ``OPENAI_MODEL`` environment variable, then
                         ``gpt-4o``.
            temperature: Sampling temperature forwarded to ``ChatOpenAI``.
        """
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4o")
        self._temperature = temperature

    async def generate(
        self,
        output_schema: type[BaseModel],
        prompt_template: str,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Render *prompt_template*, call ChatOpenAI with structured output, dump to dict.

        The chain is: ``ChatPromptTemplate`` → ``ChatOpenAI`` bound to
        *schema* via ``.with_structured_output()``.  The Pydantic instance
        returned by LangChain is immediately converted to a plain dictionary
        so callers stay decoupled from Pydantic.

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
            "LangChainOpenAIEngine.generate | model=%s schema=%s",
            self._model,
            output_schema.__name__,
        )

        llm = ChatOpenAI(model=self._model, temperature=self._temperature)
        structured_llm = llm.with_structured_output(output_schema)
        prompt = ChatPromptTemplate.from_template(prompt_template)
        chain = prompt | structured_llm

        result = await chain.ainvoke(inputs)

        if not isinstance(result, BaseModel):
            raise ValueError(
                f"Expected a Pydantic model from structured output, got {type(result)}"
            )

        return result.model_dump()
