from __future__ import annotations

import pytest
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from backend.core.llm import EngineFactory

load_dotenv()


class YesNo(BaseModel):
    reasoning: str = Field(description="The LLM's reasoning process.")
    answer: bool = Field(description="True if yes, False if no")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_azure_openai_engine_easy() -> None:
    engine = EngineFactory.create("langchain-azure-openai", temperature=0)
    result = await engine.generate_structured(
        YesNo, [HumanMessage(content="Is 2 + 2 equal to 4?")]
    )
    assert result.answer is True
    print(f"\nResult: {result}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_azure_openai_engine_generate_with_tools() -> None:
    @tool
    def get_word_length(word: str) -> int:
        """Return the number of characters in a word."""
        return len(word)

    engine = EngineFactory.create("langchain-azure-openai", temperature=0)
    response = await engine.generate_with_tools(
        [get_word_length],
        [HumanMessage(content="How many characters are in the word 'hello'?")],
    )
    assert isinstance(response, BaseMessage)
    assert response.tool_calls  # model should request the tool
    print(f"\nResponse: {response}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_azure_openai_engine_difficult() -> None:
    engine = EngineFactory.create("langchain-azure-openai", temperature=0)
    result = await engine.generate_structured(
        YesNo,
        [HumanMessage(content="Is capitalism better than communism from both economic and social perspectives?")],
    )
    assert isinstance(result.answer, bool)
    print(f"\nResult: {result}")
