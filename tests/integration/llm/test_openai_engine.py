from __future__ import annotations

import pytest
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from backend.core.llm import EngineFactory

load_dotenv()


class YesNo(BaseModel):
    reasoning: str = Field(description="The LLM's reasoning process.")
    answer: bool = Field(description="True if yes, False if no")


PROMPT = "Answer the following question: {question}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openai_engine_easy() -> None:
    engine = EngineFactory.create("langchain-openai", temperature=0)
    result = await engine.generate(YesNo, PROMPT, {"question": "Is 2 + 2 equal to 4?"})
    assert result["answer"] is True
    print(f"\nResult: {result}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openai_engine_difficult() -> None:
    engine = EngineFactory.create("langchain-openai", temperature=0)
    result = await engine.generate(
        YesNo, PROMPT, {"question": "Is capitalism better than communism from both economic and social perspectives?"}
    )
    assert isinstance(result["answer"], bool)
    print(f"\nResult: {result}")
