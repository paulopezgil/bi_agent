from __future__ import annotations

from backend.agent.config.state import AgentState
from backend.core.logger import get_logger

logger = get_logger(__name__)


async def summarize(state: AgentState) -> AgentState:
    """Pass-through node used to make successful tool-routing explicit."""
    logger.info("Node transition: summarize")
    return {
        "retry_count": state.get("retry_count", 0),
    }
