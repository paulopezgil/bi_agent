from __future__ import annotations

import uvicorn


def main() -> None:
    uvicorn.run(
        "backend.agent.app:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        # workers=1: _TOOLS_CACHE/_TOOLS_STACK in mcp/client.py are process-scoped.
        # Scale horizontally at the container level, not via multiple workers.
        workers=1,
    )


if __name__ == "__main__":
    main()
