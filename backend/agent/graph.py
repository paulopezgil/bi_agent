from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from backend.agent.state import AgentState
from backend.core.logger import get_logger
from backend.mcp.client import get_db_tools
from .nodes.call_model import call_model
from .nodes.guardrail_node import guardrail_node
from .nodes.handle_tool_result import handle_tool_result
from .nodes.should_continue import should_continue

logger = get_logger(__name__)

async def compile_graph():
    """Compile and return the plan-and-execute workflow."""
    tools = await get_db_tools()
    execute_tools = ToolNode(tools)

    workflow = StateGraph(AgentState)
    workflow.add_node("guardrail_node", guardrail_node)
    workflow.add_node("call_model", call_model)
    workflow.add_node("execute_tools", execute_tools)
    workflow.add_node("handle_tool_result", handle_tool_result)

    workflow.add_edge(START, "guardrail_node")
    workflow.add_edge("guardrail_node", "call_model")
    workflow.add_conditional_edges(
        "call_model",
        should_continue,
        {
            "execute_tools": "execute_tools",
            "end": END,
        },
    )
    workflow.add_edge("execute_tools", "handle_tool_result")
    workflow.add_edge("handle_tool_result", "call_model")

    logger.info("Compiled LangGraph workflow")
    return workflow.compile()