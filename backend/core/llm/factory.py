from __future__ import annotations

from backend.core.llm.base import LLMEngine
from backend.core.llm.engines.langchain_openai import LangChainOpenAIEngine

# Registry maps config strings to engine classes.
# Adding a new engine: import its class and add one line here.
_REGISTRY: dict[str, type[LLMEngine]] = {
    "langchain-openai": LangChainOpenAIEngine,
}


class EngineFactory:
    """Instantiates ``LLMEngine`` implementations from a configuration string.

    Separation of Concerns: the factory is the *only* place that knows which
    concrete engines exist.  Callers (nodes, services) receive an ``LLMEngine``
    and never need to import a concrete class themselves, keeping the graph
    nodes free of provider-specific imports.

    Example::

        engine = EngineFactory.create("langchain-openai", model="gpt-4o-mini")
        result = await engine.generate(MySchema, "Summarise: {text}", {"text": "..."})
    """

    @staticmethod
    def create(engine_type: str, **kwargs: object) -> LLMEngine:
        """Return a configured ``LLMEngine`` instance.

        Args:
            engine_type: A registry key identifying the desired engine.
                         Currently supported: ``"langchain-openai"``.
            **kwargs:    Forwarded verbatim to the engine's ``__init__``.
                         For ``LangChainOpenAIEngine`` these are ``model``
                         and ``temperature``.

        Returns:
            A ready-to-use ``LLMEngine`` instance.

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
    def available() -> list[str]:
        """Return the list of registered engine type keys."""
        return list(_REGISTRY)
