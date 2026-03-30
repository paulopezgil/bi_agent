from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMEngine(ABC):
    """Abstract base for all LLM execution strategies.

    Subclasses implement ``_build_llm`` to construct the provider-specific
    ``BaseChatModel``.  The two concrete methods here cover the two usage
    patterns in the agent:

    - ``generate_structured``: safety classification and any other call that
      needs a typed response bound to a Pydantic schema.
    - ``generate_with_tools``: the database-querying step where the model
      must be able to invoke tools.

    Subclass ``__init__`` convention
    --------------------------------
    Each subclass must store its configuration attributes **before** calling
    ``super().__init__()``, because the base constructor immediately calls
    ``_build_llm()``.

    Example::

        class MyEngine(LLMEngine):
            def __init__(self, model: str | None = None) -> None:
                self._model = model or "default-model"
                super().__init__()          # triggers _build_llm()

            def _build_llm(self) -> BaseChatModel:
                return SomeProvider(model=self._model)
    """

    def __init__(self) -> None:
        self._llm = self._build_llm()

    @abstractmethod
    def _build_llm(self) -> BaseChatModel:
        """Construct and return the provider-specific chat model."""

    async def generate_structured(
        self,
        output_schema: type[T],
        messages: list[BaseMessage],
    ) -> T:
        """Invoke the model and parse the response into *output_schema*.

        Args:
            output_schema: Pydantic model class describing the expected output.
            messages:      Conversation history passed directly to the model.

        Returns:
            A validated instance of *output_schema*.
        """
        return await self._llm.with_structured_output(output_schema).ainvoke(messages)

    async def generate_with_tools(
        self,
        tools: list,
        messages: list[BaseMessage],
    ) -> BaseMessage:
        """Invoke the model with *tools* bound and return the raw message.

        Args:
            tools:    LangChain-compatible tool list to bind to the model.
            messages: Conversation history passed directly to the model.

        Returns:
            The model's ``BaseMessage`` response (typically an ``AIMessage``
            that may contain tool call requests).
        """
        return await self._llm.bind_tools(tools).ainvoke(messages)
