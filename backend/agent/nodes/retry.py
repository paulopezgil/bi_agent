from __future__ import annotations

from langchain_core.messages import SystemMessage

from backend.agent.config.state import AgentState
from backend.core.logger import get_logger

logger = get_logger(__name__)


async def retry(state: AgentState) -> AgentState:
    """Increment retry count and instruct the model to repair SQL."""
    current_retry_count = state.get("retry_count", 0)
    next_retry_count = current_retry_count + 1
    logger.info("Node transition: retry (%d/3)", next_retry_count)

    return {
        "retry_count": next_retry_count,
        "messages": [
            SystemMessage(
                content=(
                    "The previous SQL execution failed with a Postgres Error. "
                    "Fix the SQL and call the appropriate tool again. "
                    f"Retry attempt: {next_retry_count}/3."
                )
            )
        ],
    }
