from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from backend.agent.api.routes import router
from backend.agent.graph import compile_graph
from backend.core.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Startup: compiling LangGraph workflow...")
    app.state.graph = await compile_graph()
    logger.info("Startup: graph ready")
    yield
    logger.info("Shutdown: releasing resources")
    app.state.graph = None


def create_app() -> FastAPI:
    app = FastAPI(title="BI Agent API", version="1.0.0", lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()
