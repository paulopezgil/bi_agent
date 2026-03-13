from __future__ import annotations

from typing import Any, TypedDict

import httpx
from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    question: str
    sql: str
    retries: int
    error: str
    rows: list[dict[str, Any]]
    answer: str


def _generate_sql(question: str, retries: int, error: str) -> str:
    text = question.lower()

    if retries > 0 and error:
        return "SELECT * FROM customers LIMIT 5"

    if "how many" in text or "count" in text:
        return "SELECT COUNT(*) AS total_customers FROM customers"
    if "orders" in text and "recent" in text:
        return "SELECT * FROM orders ORDER BY order_date DESC LIMIT 10"
    if "products" in text:
        return "SELECT * FROM products LIMIT 10"
    return "SELECT * FROM customers LIMIT 10"


async def _run_mcp_query(mcp_base_url: str, query: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            f"{mcp_base_url}/tools/execute_readonly_query",
            json={"query": query},
        )
        response.raise_for_status()
        return response.json()


def build_agent_graph(mcp_base_url: str):
    async def planner(state: AgentState) -> AgentState:
        next_state = dict(state)
        next_state["sql"] = _generate_sql(state["question"], state["retries"], state["error"])
        return next_state

    async def execute_query(state: AgentState) -> AgentState:
        next_state = dict(state)
        result = await _run_mcp_query(mcp_base_url, state["sql"])

        if result.get("ok"):
            next_state["rows"] = result.get("rows", [])
            next_state["error"] = ""
        else:
            next_state["error"] = str(result.get("error", "Unknown query error"))

        return next_state

    async def error_handler(state: AgentState) -> AgentState:
        next_state = dict(state)
        next_state["retries"] = state["retries"] + 1
        return next_state

    async def format_answer(state: AgentState) -> AgentState:
        next_state = dict(state)
        if state["error"]:
            next_state["answer"] = (
                f"I could not complete the query after {state['retries']} retries. Error: {state['error']}"
            )
        elif not state["rows"]:
            next_state["answer"] = "Query executed successfully, but no rows were returned."
        else:
            next_state["answer"] = f"Query executed successfully and returned {len(state['rows'])} rows."
        return next_state

    def should_retry(state: AgentState) -> str:
        if state["error"] and state["retries"] < 3:
            return "retry"
        return "done"

    graph = StateGraph(AgentState)
    graph.add_node("planner", planner)
    graph.add_node("execute_query", execute_query)
    graph.add_node("error_handler", error_handler)
    graph.add_node("format_answer", format_answer)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "execute_query")
    graph.add_conditional_edges(
        "execute_query",
        should_retry,
        {
            "retry": "error_handler",
            "done": "format_answer",
        },
    )
    graph.add_edge("error_handler", "planner")
    graph.add_edge("format_answer", END)

    return graph.compile()
