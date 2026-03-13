from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.graph import AgentState, build_agent_graph

app = FastAPI(title="AI Analyst Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://mcp:8001")
GRAPH = build_agent_graph(MCP_BASE_URL)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sql: str
    retries: int
    rows: list[dict[str, Any]]
    error: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "agent"}


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    initial_state: AgentState = {
        "question": payload.message,
        "sql": "",
        "retries": 0,
        "error": "",
        "rows": [],
        "answer": "",
    }
    result = await GRAPH.ainvoke(initial_state)
    return ChatResponse(**result)
