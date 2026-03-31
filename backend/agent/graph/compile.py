from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from backend.agent.graph.state import AgentState
from backend.agent.nodes.guardrail import make_guardrail_node
from backend.agent.nodes.query_database import make_query_database_node
from backend.agent.nodes.retry import retry
from backend.agent.nodes.security_warning import security_warning
from backend.agent.nodes.summarize import summarize
from backend.agent.routers.guardrail import route_after_guardrail
from backend.agent.routers.query_database import route_after_query_database
from backend.agent.routers.tool_execution import route_after_tool_execution
from backend.core.llm.factory import EngineFactory
from backend.core.logger import get_logger
from backend.mcp.client import get_db_tools

logger = get_logger(__name__)


async def compile_graph():
    """Compile and return the plan-and-execute workflow."""
    tools = await get_db_tools()
    engine = EngineFactory.create_default()

    execute_tools = ToolNode(tools)

    workflow = StateGraph(AgentState)
    workflow.add_node("guardrail", make_guardrail_node(engine))
    workflow.add_node("query_database", make_query_database_node(tools, engine))
    workflow.add_node("execute_tools", execute_tools)
    workflow.add_node("retry", retry)
    workflow.add_node("security_warning", security_warning)
    workflow.add_node("summarize", summarize)

    workflow.add_edge(START, "guardrail")
    workflow.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
        {
            "query_database": "query_database",
            "security_warning": "security_warning",
        },
    )
    workflow.add_edge("security_warning", END)
    workflow.add_conditional_edges(
        "query_database",
        route_after_query_database,
        {
            "execute_tools": "execute_tools",
            "end": END,
        },
    )
    workflow.add_conditional_edges(
        "execute_tools",
        route_after_tool_execution,
        {
            "retry": "retry",
            "summarize": "summarize",
        },
    )
    workflow.add_edge("retry", "query_database")
    workflow.add_edge("summarize", "query_database")

    logger.info("Compiled LangGraph workflow")
    return workflow.compile()
