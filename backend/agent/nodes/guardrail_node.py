from __future__ import annotations

import re

from backend.agent.state import AgentState
from backend.core.logger import get_logger

logger = get_logger(__name__)

_BLOCKED_PATTERNS = [
    re.compile(r"\bdrop\s+table\b", re.IGNORECASE),
    re.compile(r"\bdelete\s+from\b", re.IGNORECASE),
    re.compile(r"\btruncate\b", re.IGNORECASE),
    re.compile(r"\balter\s+table\b", re.IGNORECASE),
    re.compile(r";\s*(drop|delete|truncate|alter)\b", re.IGNORECASE),
    re.compile(r"\bunion\s+select\b", re.IGNORECASE),
    re.compile(r"--"),
]


async def guardrail_node(state: AgentState) -> AgentState:
    """Mark state as unsafe when user prompt contains suspicious SQL patterns."""
    logger.info("Node transition: guardrail_node")

    messages = state.get("messages", [])
    latest_text = ""
    if messages:
        latest = messages[-1]
        latest_text = str(getattr(latest, "content", ""))

    is_safe = not any(pattern.search(latest_text) for pattern in _BLOCKED_PATTERNS)
    if not is_safe:
        logger.warning("Guardrail blocked suspicious prompt")

    return {
        "is_safe": is_safe,
        "retry_count": state.get("retry_count", 0),
    }
