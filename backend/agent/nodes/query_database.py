from __future__ import annotations

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.messages import ToolMessage

from backend.agent.config.prompts import QUERY_DATABASE_SYSTEM_PROMPT
from backend.agent.config.state import AgentState
from backend.core.logger import get_logger
from backend.core.openai_client import get_chat_openai
from backend.mcp.client import get_db_tools
from backend.utils.parsing import parse_tool_message

logger = get_logger(__name__)


def _is_failed_tool_response(message: ToolMessage) -> bool:
    response = parse_tool_message(message)
    return (not response.ok) or (response.error is not None) or (response.code is not None)


async def query_database(state: AgentState) -> AgentState:
    """Run the primary database-querying model with DB tools bound."""
    logger.info("Node transition: query_database")

    retry_count = state.get("retry_count", 0)
    last_message = state.get("messages", [])[-1] if state.get("messages") else None
    if (
        retry_count >= 3
        and isinstance(last_message, ToolMessage)
        and _is_failed_tool_response(last_message)
    ):
        logger.warning("Retry budget exhausted after database errors")
        return {
            "messages": [
                AIMessage(
                    content=(
                        "I could not produce a valid SQL query after 3 retry attempts. "
                        "Please rephrase your question or provide more schema context."
                    )
                )
            ]
        }

    tools = await get_db_tools()
    llm = get_chat_openai(temperature=0)
    model_with_tools = llm.bind_tools(tools)

    response = await model_with_tools.ainvoke(
        [SystemMessage(content=QUERY_DATABASE_SYSTEM_PROMPT), *state["messages"]]
    )

    if isinstance(response, AIMessage) and response.tool_calls:
        logger.info("query_database requested %d tool call(s)", len(response.tool_calls))
    else:
        logger.info("query_database produced final response")

    return {"messages": [response]}
