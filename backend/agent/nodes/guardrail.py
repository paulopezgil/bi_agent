from __future__ import annotations

import os

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from backend.agent.config.prompts import GUARDRAIL_SYSTEM_PROMPT
from backend.agent.config.state import AgentState
from backend.core.logger import get_logger
from backend.core.openai_client import get_chat_openai

logger = get_logger(__name__)


class GuardrailDecision(BaseModel):
    is_safe: bool = Field(description="Whether the user request is safe to process")
    reason: str = Field(description="Short explanation of the safety decision")


def _message_content_to_text(content: str | list) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
            else:
                parts.append(str(item))
        return "\n".join(parts).strip()

    return str(content)


async def guardrail(state: AgentState) -> AgentState:
    """Use an LLM classifier to determine whether the request is safe."""
    logger.info("Node transition: guardrail")

    messages = state.get("messages", [])
    latest_text = ""
    if messages:
        latest = messages[-1]
        latest_text = _message_content_to_text(getattr(latest, "content", ""))

    if not latest_text.strip():
        logger.warning("Guardrail received empty input, marking unsafe")
        return {
            "is_safe": False,
            "retry_count": state.get("retry_count", 0),
        }

    guardrail_model = os.getenv("OPENAI_GUARDRAIL_MODEL", "gpt-4o-mini")

    try:
        llm = get_chat_openai(model=guardrail_model, temperature=0)
        classifier = llm.with_structured_output(GuardrailDecision)
        decision = await classifier.ainvoke(
            [
                SystemMessage(content=GUARDRAIL_SYSTEM_PROMPT),
                HumanMessage(content=latest_text),
            ]
        )

        if not decision.is_safe:
            logger.warning("Guardrail blocked request: %s", decision.reason)
        else:
            logger.info("Guardrail allowed request")

        return {
            "is_safe": decision.is_safe,
            "retry_count": state.get("retry_count", 0),
        }
    except Exception as exc:  # pragma: no cover - network/provider dependent
        logger.exception("Guardrail classification failed, marking unsafe: %s", exc)
        return {
            "is_safe": False,
            "retry_count": state.get("retry_count", 0),
        }

