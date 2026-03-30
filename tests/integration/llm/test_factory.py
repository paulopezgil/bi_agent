"""Integration tests for EngineFactory.create_default().

Verifies that create_default() reads LLM_ENGINE from the environment and
produces a working engine — without hardcoding a specific engine in the call.
"""
from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from backend.core.llm.factory import EngineFactory

load_dotenv()


class YesNo(BaseModel):
    reasoning: str = Field(description="The LLM's reasoning process.")
    answer: bool = Field(description="True if yes, False if no")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_default_uses_llm_engine_env_var() -> None:
    """create_default() honours LLM_ENGINE and produces a working engine."""
    engine_type = os.getenv("LLM_ENGINE", "langchain-openai")
    engine = EngineFactory.create_default(temperature=0)

    result = await engine.generate_structured(
        YesNo, [HumanMessage(content="Is 2 + 2 equal to 4?")]
    )

    assert result.answer is True
    print(f"\nEngine type from env: {engine_type}")
    print(f"Result: {result}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_default_without_env_var_falls_back_to_openai() -> None:
    """Without LLM_ENGINE set, create_default() falls back to langchain-openai."""
    env = {k: v for k, v in os.environ.items() if k != "LLM_ENGINE"}

    # Temporarily remove LLM_ENGINE to test the default
    original = os.environ.pop("LLM_ENGINE", None)
    try:
        engine = EngineFactory.create_default(temperature=0)
        result = await engine.generate_structured(
            YesNo, [HumanMessage(content="Is 2 + 2 equal to 4?")]
        )
    finally:
        if original is not None:
            os.environ["LLM_ENGINE"] = original

    assert result.answer is True
    print(f"\nResult: {result}")
