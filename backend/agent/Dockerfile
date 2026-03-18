FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY agent/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Keep full backend package available so current stdio MCP client path works unchanged.
COPY . /app/backend

EXPOSE 8000

# Temporary runtime check until agent API entrypoint is added.
CMD ["python", "-m", "backend.agent.graph"]
