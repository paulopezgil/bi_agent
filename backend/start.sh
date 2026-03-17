#!/bin/sh
set -e

# Start MCP server on localhost only (not exposed externally)
cd /app/mcp && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 &

# Start agent server in the foreground (process 1 for Docker signal handling)
cd /app/agent && exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
