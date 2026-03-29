from __future__ import annotations

from backend.agent.graph import run_once_sync


class FakeClient:
    def __init__(self) -> None:
        self.calls = 0

    async def list_tables(self) -> list[str]:
        return ["customers"]

    async def describe_table(self, table_name: str) -> dict:
        return {"table_name": table_name, "columns": [], "foreign_keys": []}

    async def execute_readonly_query(self, query: str) -> dict:
        self.calls += 1
        if self.calls == 1:
            return {"ok": False, "error": "relation does not exist", "code": "42P01"}
        return {"ok": True, "rows": [{"total_count": 1}], "row_count": 1}


def test_graph_retries_after_error() -> None:
    state = run_once_sync(FakeClient(), "How many customers do we have?")
    assert state["retry_count"] == 1
    assert state["last_error"] == ""
    assert state["query_result"] == [{"total_count": 1}]
