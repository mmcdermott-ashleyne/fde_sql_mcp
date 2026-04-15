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


def test_set_query_target_explicit_switch_between_onprem_and_fabric(
    monkeypatch,
) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
            "fabric_allowed_workspaces": [
                "fde_core_data_dev",
                "fde_core_data_stg",
                "fde_core_data_prod",
            ],
            "fabric_allowed_databases": ["core_dw", "core_lh"],
        },
    )
    _configure_targeting(monkeypatch, settings)

    initial = targeting.get_query_target_impl()
    assert initial["environment"] == "onprem"

    selected = targeting.set_query_target_impl(
        "fabric workspace=fde_core_data_dev endpoint=warehouse database=core_dw"
    )
    assert selected["environment"] == "fabric"
    assert selected["workspace"] == "fde_core_data_dev"
    assert selected["endpoint_type"] == "warehouse"
    assert selected["database"] == "core_dw"

    reverted = targeting.set_query_target_impl("onprem")
    assert reverted["environment"] == "onprem"
    assert reverted["endpoint_type"] == "sql_server"


def test_set_query_target_natural_language_resolves_deterministically(
    monkeypatch,
) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
            "fabric_allowed_workspaces": [
                "fde_core_data_dev",
                "fde_core_data_stg",
                "fde_core_data_prod",
            ],
            "fabric_allowed_databases": ["core_dw", "core_lh"],
        },
    )
    _configure_targeting(monkeypatch, settings)

    selected = targeting.set_query_target_impl("query fabric prod lakehouse")
    assert selected == {
        "environment": "fabric",
        "workspace": "fde_core_data_prod",
        "workspace_id": None,
        "endpoint_type": "lakehouse",
        "database": "core_lh",
    }


def test_set_query_target_workspace_id_mapping(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
            "fabric_allowed_workspaces": ["fde_core_data_dev"],
            "fabric_allowed_databases": ["core_dw"],
            "fabric_workspace_id_map": {
                "fde_core_data_dev": "11111111-1111-1111-1111-111111111111"
            },
        },
    )
    _configure_targeting(monkeypatch, settings)

    selected = targeting.set_query_target_impl(
        "fabric workspace=11111111-1111-1111-1111-111111111111 endpoint=warehouse"
    )
    assert selected["workspace"] == "fde_core_data_dev"
    assert (
        selected["workspace_id"] == "11111111-1111-1111-1111-111111111111"
    )


def test_set_query_target_rejects_workspace_outside_allowlist(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
            "fabric_allowed_workspaces": ["fde_core_data_dev"],
            "fabric_allowed_databases": ["core_dw"],
        },
    )
    _configure_targeting(monkeypatch, settings)

    try:
        targeting.set_query_target_impl(
            "fabric workspace=fde_core_data_prod endpoint=warehouse database=core_dw"
        )
    except ValueError as exc:
        assert "allowlist" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for out-of-allowlist workspace")


def test_list_fabric_workspaces_returns_allowlist_and_id_mappings(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
            "fabric_allowed_workspaces": [
                "fde_core_data_dev",
                "fde_core_data_stg",
            ],
            "fabric_workspace_id_map": {
                "fde_core_data_dev": "dev-id-123",
            },
            "fabric_default_workspace": "fde_core_data_stg",
        },
    )
    _configure_targeting(monkeypatch, settings)

    rows = targeting.list_fabric_workspaces_impl()
    assert rows == [
        {
            "workspace": "fde_core_data_dev",
            "workspace_id": "dev-id-123",
            "is_default": False,
        },
        {
            "workspace": "fde_core_data_stg",
            "workspace_id": None,
            "is_default": True,
        },
    ]


class _FakeCursor:
    def __init__(self) -> None:
        self.description = [("id",), ("name",)]

    def execute(self, _query: str, _params=None) -> None:
        return None

    def fetchall(self):
        return [(1, "alpha")]


class _FakeConnection:
    def cursor(self) -> _FakeCursor:
        return _FakeCursor()


class _FakeSqlConnection:
    @contextmanager
    def get_connection(self):
        yield _FakeConnection()


class _ConnectionRecorder:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def __call__(self, **kwargs):
        self.calls.append(kwargs)
        return _FakeSqlConnection()


def test_run_readonly_query_includes_target_context(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
            "fabric_allowed_workspaces": ["fde_core_data_dev"],
            "fabric_allowed_databases": ["core_dw"],
        },
    )
    _configure_targeting(monkeypatch, settings)
    monkeypatch.setattr(
        databases, "get_sql_connection", lambda **_kwargs: _FakeSqlConnection()
    )

    result = databases.run_readonly_query_impl("master", "SELECT 1 AS id")

    assert result["row_count"] == 1
    assert result["rows"] == [{"id": 1, "name": "alpha"}]
    assert result["target_context"]["environment"] == "onprem"
    assert result["target_context"]["endpoint_type"] == "sql_server"


def test_run_readonly_query_executes_with_fabric_warehouse_target(
    monkeypatch,
) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
            "fabric_allowed_workspaces": ["fde_core_data_dev"],
            "fabric_allowed_databases": ["core_dw"],
            "fabric_sql_endpoint_map": {
                "fde_core_data_dev": {
                    "warehouse": {
                        "server": "dev-warehouse.sql.fabric",
                        "database": "core_dw",
                        "user": "svc-user",
                        "password": "svc-pass",
                    }
                }
            },
        },
    )
    _configure_targeting(monkeypatch, settings)
    recorder = _ConnectionRecorder()
    monkeypatch.setattr(databases, "get_sql_connection", recorder)
    targeting.set_query_target_impl(
        "fabric workspace=fde_core_data_dev endpoint=warehouse database=core_dw"
    )

    result = databases.run_readonly_query_impl("core_dw", "SELECT 1")

    assert result["target_context"]["environment"] == "fabric"
    assert result["target_context"]["endpoint_type"] == "warehouse"
    assert recorder.calls == [
        {
            "server": "dev-warehouse.sql.fabric",
            "database": "core_dw",
            "username": "svc-user",
            "password": "svc-pass",
            "environment": "fabric",
        }
    ]


def test_run_readonly_query_rejects_database_mismatch_for_fabric(
    monkeypatch,
) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
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
        },
    )
    _configure_targeting(monkeypatch, settings)
    monkeypatch.setattr(
        databases, "get_sql_connection", lambda **_kwargs: _FakeSqlConnection()
    )
    targeting.set_query_target_impl(
        "fabric workspace=fde_core_data_dev endpoint=warehouse database=core_dw"
    )

    try:
        databases.run_readonly_query_impl("master", "SELECT 1")
    except ValueError as exc:
        assert "to match" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for Fabric database mismatch")


def test_list_tables_uses_fabric_lakehouse_connection(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
            "fabric_allowed_workspaces": ["fde_core_data_dev"],
            "fabric_allowed_databases": ["core_lh"],
            "fabric_sql_endpoint_map": {
                "fde_core_data_dev": {
                    "lakehouse": {
                        "server": "dev-lakehouse.sql.fabric",
                        "database": "core_lh",
                    }
                }
            },
        },
    )
    _configure_targeting(monkeypatch, settings)
    recorder = _ConnectionRecorder()
    monkeypatch.setattr(databases, "get_sql_connection", recorder)
    targeting.set_query_target_impl(
        "fabric workspace=fde_core_data_dev endpoint=lakehouse database=core_lh"
    )

    rows = databases.list_tables_impl("core_lh")

    assert rows == [{"id": 1, "name": "alpha"}]
    assert recorder.calls[0]["server"] == "dev-lakehouse.sql.fabric"
    assert recorder.calls[0]["database"] == "core_lh"


def test_list_databases_uses_routed_fabric_database(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
            "sql_database": "master",
            "fabric_allowed_workspaces": ["fde_core_data_dev"],
            "fabric_allowed_databases": ["core_lh"],
            "fabric_sql_endpoint_map": {
                "fde_core_data_dev": {
                    "lakehouse": {
                        "server": "dev-lakehouse.sql.fabric",
                        "database": "core_lh",
                    }
                }
            },
        },
    )
    _configure_targeting(monkeypatch, settings)
    recorder = _ConnectionRecorder()
    monkeypatch.setattr(databases, "get_sql_connection", recorder)
    targeting.set_query_target_impl(
        "fabric workspace=fde_core_data_dev endpoint=lakehouse database=core_lh"
    )

    rows = databases.list_databases_impl()

    assert rows == [{"id": 1, "name": "alpha"}]
    assert recorder.calls[0]["database"] == "core_lh"


def test_run_readonly_query_fails_when_fabric_mapping_missing(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
            "fabric_allowed_workspaces": ["fde_core_data_dev"],
            "fabric_allowed_databases": ["core_dw"],
        },
    )
    _configure_targeting(monkeypatch, settings)
    targeting.set_query_target_impl(
        "fabric workspace=fde_core_data_dev endpoint=warehouse database=core_dw"
    )

    try:
        databases.run_readonly_query_impl("core_dw", "SELECT 1")
    except ValueError as exc:
        assert "endpoint mapping" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for missing Fabric endpoint mapping")


def test_run_readonly_query_rejects_write_keyword_for_fabric_target(
    monkeypatch,
) -> None:
    settings = _build_settings(
        monkeypatch,
        local={
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
        },
    )
    _configure_targeting(monkeypatch, settings)
    targeting.set_query_target_impl(
        "fabric workspace=fde_core_data_dev endpoint=warehouse database=core_dw"
    )

    try:
        databases.run_readonly_query_impl("core_dw", "DELETE FROM dbo.t")
    except ValueError as exc:
        assert "only select statements" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError for non-read-only query")
