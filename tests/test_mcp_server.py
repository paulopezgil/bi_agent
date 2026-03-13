from backend.mcp_server.server import _validate_read_only_query


def test_validate_allows_select() -> None:
    assert _validate_read_only_query("SELECT * FROM customers LIMIT 1") is None


def test_validate_blocks_write_query() -> None:
    err = _validate_read_only_query("DELETE FROM customers")
    assert err is not None
    assert "read-only" in err.lower()
