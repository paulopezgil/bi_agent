from __future__ import annotations

from typing import Literal

from backend.agent.config.state import AgentState
from backend.core.logger import get_logger

logger = get_logger(__name__)


def route_after_guardrail(state: AgentState) -> Literal["query_database", "security_warning"]:
    """Route to DB querying node when safe, otherwise to security warning node."""
    if state.get("is_safe", True):
        logger.info("Conditional edge: guardrail_node -> query_database")
        return "query_database"

    logger.info("Conditional edge: guardrail_node -> security_warning")
    return "security_warning"
