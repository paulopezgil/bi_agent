from __future__ import annotations

from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from backend.agent.prompts import SYSTEM_PROMPT
from backend.agent.state import AgentState
from backend.core.logger import get_logger
from backend.core.openai_client import get_chat_openai
from backend.mcp_client import get_db_tools

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


def should_continue(state: AgentState) -> Literal["call_tool", "end"]:
    """Route to tool execution when the model emits tool calls."""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        logger.info("Conditional edge: call_model -> call_tool")
        return "call_tool"

    logger.info("Conditional edge: call_model -> END")
    return "end"


async def compile_graph():
    """Compile and return the plan-and-execute workflow."""
    tools = await get_db_tools()
    tool_node = ToolNode(tools)

    workflow = StateGraph(AgentState)
    workflow.add_node("call_model", call_model)
    workflow.add_node("call_tool", tool_node)

    workflow.add_edge(START, "call_model")
    workflow.add_conditional_edges(
        "call_model",
        should_continue,
        {
            "call_tool": "call_tool",
            "end": END,
        },
    )
    workflow.add_edge("call_tool", "call_model")

    logger.info("Compiled LangGraph workflow")
    return workflow.compile()
