from __future__ import annotations

from types import SimpleNamespace

from fde_sql_mcp.clients import sql


def _stub_settings(**overrides: object) -> SimpleNamespace:
    values = {
        "sql_driver": "{ODBC Driver 17 for SQL Server}",
        "sql_server_port": None,
        "sql_encrypt": True,
        "sql_trust_server_certificate": True,
        "sql_connection_timeout": 30,
        "sql_application_intent": "ReadOnly",
        "fabric_auth_mode": "default_browser",
        "fabric_client_id": None,
        "fabric_client_secret": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_onprem_without_credentials_uses_trusted_connection(monkeypatch) -> None:
    monkeypatch.setattr(sql, "settings", _stub_settings())
    conn = sql.SQLServerConnection(
        server="onprem-sql",
        database="master",
        driver="{ODBC Driver 17 for SQL Server}",
        environment="onprem",
    )

    conn_str = conn._build_conn_str()

    assert "Trusted_Connection=yes;" in conn_str
    assert "Authentication=ActiveDirectoryInteractive;" not in conn_str


def test_fabric_without_credentials_uses_interactive_auth(monkeypatch) -> None:
    monkeypatch.setattr(
        sql, "settings", _stub_settings(fabric_auth_mode="default_browser")
    )
    conn = sql.SQLServerConnection(
        server="dev-warehouse.sql.fabric.microsoft.com",
        database="core_dw",
        driver="{ODBC Driver 17 for SQL Server}",
        environment="fabric",
    )

    conn_str = conn._build_conn_str()

    assert "Authentication=ActiveDirectoryInteractive;" in conn_str
    assert "Trusted_Connection=yes;" not in conn_str


def test_fabric_client_secret_mode_uses_service_principal(monkeypatch) -> None:
    monkeypatch.setattr(
        sql,
        "settings",
        _stub_settings(
            fabric_auth_mode="client_secret",
            fabric_client_id="app-client-id",
            fabric_client_secret="app-client-secret",
        ),
    )
    conn = sql.SQLServerConnection(
        server="dev-warehouse.sql.fabric.microsoft.com",
        database="core_dw",
        driver="{ODBC Driver 17 for SQL Server}",
        environment="fabric",
    )

    conn_str = conn._build_conn_str()

    assert "Authentication=ActiveDirectoryServicePrincipal;" in conn_str
    assert "Uid=app-client-id;" in conn_str
    assert "Pwd=app-client-secret;" in conn_str
    assert "Trusted_Connection=yes;" not in conn_str


def test_fabric_client_secret_mode_requires_credentials(monkeypatch) -> None:
    monkeypatch.setattr(
        sql, "settings", _stub_settings(fabric_auth_mode="client_secret")
    )
    conn = sql.SQLServerConnection(
        server="dev-warehouse.sql.fabric.microsoft.com",
        database="core_dw",
        driver="{ODBC Driver 17 for SQL Server}",
        environment="fabric",
    )

    try:
        conn._build_conn_str()
    except RuntimeError as exc:
        assert "not fully configured" in str(exc).lower()
    else:
        raise AssertionError(
            "Expected RuntimeError when client-secret Fabric auth is incomplete."
        )
