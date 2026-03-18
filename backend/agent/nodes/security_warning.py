from __future__ import annotations

from langchain_core.messages import AIMessage

from backend.agent.config.state import AgentState
from backend.core.logger import get_logger

logger = get_logger(__name__)


async def security_warning(state: AgentState) -> AgentState:
    """Return a final security warning when guardrails mark input unsafe."""
    logger.warning("Node transition: security_warning")
    return {
        "messages": [
            AIMessage(
                content=(
                    "Security Warning: The request appears unsafe and may contain "
                    "destructive or injection-like SQL instructions."
                )
            )
        ]
    }
