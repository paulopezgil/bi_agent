from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel

class LLMEngine(ABC):
    """Abstract base for all LLM execution strategies.

    Separation of Concerns: this contract decouples *what* is requested
    (a schema + a prompt template + inputs) from *how* it is fulfilled
    (which model provider, which SDK, which retry policy).  Callers depend
    only on this interface; swapping providers requires no changes outside
    the concrete engine and the factory.
    """

    @abstractmethod
    async def generate(
        self,
        output_schema: BaseModel,
        prompt_template: str,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Render *prompt_template* with *inputs*, invoke the LLM, and return a dict.

        Args:
            output_schema:   A Pydantic model class that describes the expected output
                             structure.  Engines use this for structured-output binding.
            prompt_template: A prompt string that may contain ``{key}`` placeholders
                             matching the keys in *inputs*.
            inputs:          Values substituted into *prompt_template* before the call.

        Returns:
            The model's response serialised as a plain Python dictionary via
            ``model_dump()``, so callers never need to import Pydantic.
        """
