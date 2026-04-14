from __future__ import annotations

from contextlib import contextmanager

from fde_sql_mcp import config as cfg
from fde_sql_mcp.tools import databases
from fde_sql_mcp.tools import targeting

_ENV_KEYS = [
    "SQL_SERVER_HOST",
    "SQL_SERVER_PORT",
    "SQL_SERVER_DATABASE",
    "SQL_DRIVER",
    "SQL_APPLICATION_INTENT",
    "SQL_ENCRYPT",
    "SQL_TRUST_SERVER_CERTIFICATE",
    "SQL_CONNECTION_TIMEOUT",
    "SQL_QUERY_TIMEOUT",
    "SQL_MAX_ROWS",
    "SQL_MAX_QUERY_CHARS",
    "SQL_ENFORCE_READONLY",
    "FABRIC_ENABLED",
    "FABRIC_TENANT_ID",
    "FABRIC_CLIENT_ID",
    "FABRIC_CLIENT_SECRET",
    "FABRIC_AUTH_FALLBACK_MODE",
    "FABRIC_DEFAULT_WORKSPACE",
    "FABRIC_DEFAULT_DATABASE",
    "FABRIC_WORKSPACE_ID_MAP",
    "FABRIC_ALLOWED_WORKSPACES",
    "FABRIC_ALLOWED_DATABASES",
    "FABRIC_SQL_ENDPOINT_MAP",
]


def _build_settings(
    monkeypatch, *, local: dict[str, object] | None = None
) -> cfg.Settings:
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    monkeypatch.setenv("SQL_SERVER_HOST", "test-sql-host")
    monkeypatch.setattr(cfg, "_LOCAL_SETTINGS", dict(local or {}))
    return cfg.Settings()


def _configure_targeting(monkeypatch, settings: cfg.Settings) -> None:
    monkeypatch.setattr(targeting, "settings", settings)
    monkeypatch.setattr(databases, "settings", settings)
    targeting.reset_query_target_impl()


class _FakeCursor:
    def __init__(self, rows=None) -> None:
        self.description = [("id",), ("name",)]
        self.timeout = None
        self.executed: list[str] = []
        self._rows = list(rows or [(1, "alpha"), (2, "beta"), (3, "gamma")])

    def execute(self, query: str, _params=None) -> None:
        self.executed.append(query)

    def fetchall(self):
        return list(self._rows)


class _FakeConnection:
    def __init__(self, cursor: _FakeCursor) -> None:
        self._cursor = cursor

    def cursor(self) -> _FakeCursor:
        return self._cursor


class _FakeSqlConnection:
    def __init__(self, cursor: _FakeCursor) -> None:
        self._cursor = cursor

    @contextmanager
    def get_connection(self):
        yield _FakeConnection(self._cursor)


class _ConnectionRecorder:
    def __init__(self, cursor: _FakeCursor) -> None:
        self.cursor = cursor
        self.calls: list[dict[str, object]] = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return _FakeSqlConnection(self.cursor)


def _base_local_settings() -> dict[str, object]:
    return {
        "sql_query_timeout": 42,
        "sql_max_rows": 2,
        "sql_max_query_chars": 12,
        "fabric_allowed_workspaces": ["fde_core_data_dev"],
        "fabric_allowed_databases": ["core_dw"],
        "fabric_sql_endpoint_map": {
            "fde_core_data_dev": {
                "warehouse": {
                    "server": "dev-warehouse.sql.fabric",
                    "database": "core_dw",
                }
            }
        },
    }


def test_readonly_validator_rejects_write_sql_for_onprem_and_fabric(
    monkeypatch,
) -> None:
    settings = _build_settings(monkeypatch, local=_base_local_settings())
    _configure_targeting(monkeypatch, settings)

    for target_hint, database in (
        ("onprem", "master"),
        ("fabric workspace=fde_core_data_dev endpoint=warehouse database=core_dw", "core_dw"),
    ):
        targeting.set_query_target_impl(target_hint)
        try:
            databases.run_readonly_query_impl(database, "DELETE t")
        except ValueError as exc:
            assert "only select statements" in str(exc).lower()
        else:
            raise AssertionError("Expected ValueError for write SQL")


def test_max_query_length_rejected_before_connection_for_both_targets(
    monkeypatch,
) -> None:
    settings = _build_settings(monkeypatch, local=_base_local_settings())
    _configure_targeting(monkeypatch, settings)

    def _unexpected_connection(**_kwargs):
        raise AssertionError("Query length should fail before any connection is created.")

    monkeypatch.setattr(databases, "get_sql_connection", _unexpected_connection)

    too_long_query = "SELECT 1234567890"
    for target_hint, database in (
        ("onprem", "master"),
        ("fabric workspace=fde_core_data_dev endpoint=warehouse database=core_dw", "core_dw"),
    ):
        targeting.set_query_target_impl(target_hint)
        try:
            databases.run_readonly_query_impl(database, too_long_query)
        except ValueError as exc:
            assert "maximum allowed length" in str(exc).lower()
        else:
            raise AssertionError("Expected ValueError for oversized query")


def test_max_rows_clamped_to_settings_limit_on_both_targets(monkeypatch) -> None:
    settings = _build_settings(monkeypatch, local=_base_local_settings())
    _configure_targeting(monkeypatch, settings)

    for target_hint, database in (
        ("onprem", "master"),
        ("fabric workspace=fde_core_data_dev endpoint=warehouse database=core_dw", "core_dw"),
    ):
        cursor = _FakeCursor(rows=[(1, "alpha"), (2, "beta")])
        recorder = _ConnectionRecorder(cursor)
        monkeypatch.setattr(databases, "get_sql_connection", recorder)
        targeting.set_query_target_impl(target_hint)

        result = databases.run_readonly_query_impl(database, "SELECT 1", max_rows=999)
        assert result["row_limit"] == 2
        assert result["truncated"] is True
        assert "SET ROWCOUNT 2" in cursor.executed[0]


def test_timeout_applied_to_query_and_metadata_paths_for_both_targets(
    monkeypatch,
) -> None:
    settings = _build_settings(monkeypatch, local=_base_local_settings())
    _configure_targeting(monkeypatch, settings)

    for target_hint, database in (
        ("onprem", "master"),
        ("fabric workspace=fde_core_data_dev endpoint=warehouse database=core_dw", "core_dw"),
    ):
        query_cursor = _FakeCursor(rows=[(1, "alpha")])
        query_recorder = _ConnectionRecorder(query_cursor)
        monkeypatch.setattr(databases, "get_sql_connection", query_recorder)
        targeting.set_query_target_impl(target_hint)

        databases.run_readonly_query_impl(database, "SELECT 1")
        assert query_cursor.timeout == 42

        metadata_cursor = _FakeCursor(rows=[(1, "alpha")])
        metadata_recorder = _ConnectionRecorder(metadata_cursor)
        monkeypatch.setattr(databases, "get_sql_connection", metadata_recorder)

        databases.list_tables_impl(database)
        assert metadata_cursor.timeout == 42
