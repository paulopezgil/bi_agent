from __future__ import annotations
from backend.agent.state import AgentState
from langchain_core.messages import AIMessage, SystemMessage

from backend.core.logger import get_logger
from backend.mcp.client import get_db_tools
from backend.agent.prompts import SYSTEM_PROMPT
from backend.core.openai_client import get_chat_openai


logger = get_logger(__name__)

async def call_model(state: AgentState) -> AgentState:
    """Invoke the LLM with tools bound for plan-and-execute behavior."""
    logger.info("Node transition: call_model")

    tools = await get_db_tools()
    llm = get_chat_openai(temperature=0)
    model_with_tools = llm.bind_tools(tools)

    response = await model_with_tools.ainvoke(
        [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    )

    if isinstance(response, AIMessage) and response.tool_calls:
        logger.info("call_model requested %d tool call(s)", len(response.tool_calls))
    else:
        logger.info("call_model produced final response")

    return {"messages": [response]}