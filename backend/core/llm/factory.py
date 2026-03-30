from __future__ import annotations

import os

from backend.core.llm.base import LLMEngine
from backend.core.llm.engines.langchain_anthropic import LangChainAnthropicEngine
from backend.core.llm.engines.langchain_azure_openai import LangChainAzureOpenAIEngine
from backend.core.llm.engines.langchain_openai import LangChainOpenAIEngine

# Registry maps config strings to engine classes.
# Adding a new engine: import its class and add one line here.
_REGISTRY = {
    "langchain-anthropic": LangChainAnthropicEngine,
    "langchain-azure-openai": LangChainAzureOpenAIEngine,
    "langchain-openai": LangChainOpenAIEngine,
}


class EngineFactory:
    """Instantiates ``LLMEngine`` implementations from a configuration string.

    The active engine is selected via the ``LLM_ENGINE`` environment variable.
    Supported values: ``"langchain-openai"``, ``"langchain-azure-openai"``,
    ``"langchain-anthropic"``.

    Example::

        engine = EngineFactory.create_default()
        decision = await engine.generate_structured(MySchema, messages)
    """

    @staticmethod
    def create(engine_type: str, **kwargs: object) -> LLMEngine:
        """Return a configured ``LLMEngine`` instance for *engine_type*.

        Args:
            engine_type: A registry key identifying the desired engine.
            **kwargs:    Forwarded to the engine's ``__init__``.

        Raises:
            ValueError: If *engine_type* is not in the registry.
        """
        engine_cls = _REGISTRY.get(engine_type)
        if engine_cls is None:
            supported = ", ".join(f'"{k}"' for k in _REGISTRY)
            raise ValueError(
                f"Unknown engine type {engine_type!r}. Supported: {supported}"
            )
        return engine_cls(**kwargs)

    @staticmethod
    def create_default(**kwargs: object) -> LLMEngine:
        """Return an engine for the type set in ``LLM_ENGINE`` (default: ``langchain-openai``).

        Args:
            **kwargs: Forwarded to the engine's ``__init__``. Use ``model``
                      to override the model/deployment for all engine types.
        """
        engine_type = os.getenv("LLM_ENGINE", "langchain-openai")
        return EngineFactory.create(engine_type, **kwargs)

    @staticmethod
    def available() -> list[str]:
        """Return the list of registered engine type keys."""
        return list(_REGISTRY)
