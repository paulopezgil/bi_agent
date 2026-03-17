from __future__ import annotations
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from backend.agent.prompts import SYSTEM_PROMPT
from backend.agent.state import AgentState
from backend.core.logger import get_logger
from backend.mcp.client import get_db_tools
from .nodes.call_model import call_model
from .nodes.should_continue import should_continue

logger = get_logger(__name__)

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