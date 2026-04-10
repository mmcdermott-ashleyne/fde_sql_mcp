from __future__ import annotations

import json

from fde_sql_mcp import config as cfg
from fde_sql_mcp.tools import auth

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
    "FABRIC_ALLOWED_WORKSPACES",
    "FABRIC_ALLOWED_DATABASES",
]


def _build_settings(
    monkeypatch,
    *,
    local: dict[str, object] | None = None,
    env: dict[str, str] | None = None,
) -> cfg.Settings:
    for key in _ENV_KEYS:
        monkeypatch.delenv(key, raising=False)

    merged_env = {"SQL_SERVER_HOST": "test-sql-host"}
    if env:
        merged_env.update(env)
    for key, value in merged_env.items():
        monkeypatch.setenv(key, value)

    monkeypatch.setattr(cfg, "_LOCAL_SETTINGS", dict(local or {}))
    return cfg.Settings()


def test_existing_sql_defaults_preserved(monkeypatch) -> None:
    settings = _build_settings(monkeypatch)

    assert settings.sql_database == "master"
    assert settings.sql_application_intent == "ReadOnly"
    assert settings.sql_max_rows == 200
    assert settings.sql_query_timeout == 30
    assert settings.fabric_auth_mode == "default_browser"


def test_existing_sql_defaults_local_precedence(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        local={"sql_database": "analytics", "sql_max_rows": 50},
        env={"SQL_SERVER_DATABASE": "env_db", "SQL_MAX_ROWS": "500"},
    )

    assert settings.sql_database == "analytics"
    assert settings.sql_max_rows == 50


def test_fabric_auth_mode_client_secret_precedence(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        env={
            "FABRIC_TENANT_ID": "tenant-1",
            "FABRIC_CLIENT_ID": "client-1",
            "FABRIC_CLIENT_SECRET": "super-secret",
        },
    )

    assert settings.fabric_auth_mode == "client_secret"
    assert settings.fabric_tenant_context == "tenant-1"


def test_fabric_auth_mode_fallback_when_partial_credentials(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        env={
            "FABRIC_TENANT_ID": "tenant-2",
            "FABRIC_CLIENT_ID": "client-2",
            "FABRIC_AUTH_FALLBACK_MODE": "browser",
        },
    )

    assert settings.fabric_auth_mode == "browser"
    assert settings.fabric_tenant_context == "tenant-2"


def test_fabric_auth_mode_uses_default_fallback(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        env={"FABRIC_TENANT_ID": "tenant-3"},
    )

    assert settings.fabric_auth_mode == "default_browser"
    assert settings.fabric_tenant_context == "tenant-3"


def test_fabric_allowlists_parse_from_local_and_env(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        local={"fabric_allowed_workspaces": ["dev", "stg"]},
        env={"FABRIC_ALLOWED_DATABASES": "core_dw, core_lh"},
    )

    assert settings.fabric_allowed_workspaces == ("dev", "stg")
    assert settings.fabric_allowed_databases == ("core_dw", "core_lh")


def test_auth_diagnostics_do_not_expose_secret_values(monkeypatch) -> None:
    settings = _build_settings(
        monkeypatch,
        env={
            "FABRIC_ENABLED": "true",
            "FABRIC_TENANT_ID": "tenant-auth",
            "FABRIC_CLIENT_ID": "client-auth",
            "FABRIC_CLIENT_SECRET": "super-secret-value",
        },
    )
    monkeypatch.setattr(auth, "settings", settings)

    info = auth.get_auth_info_impl()
    payload = json.dumps(info)

    assert info["auth_mode"] == "client_secret"
    assert info["tenant_context"] == "tenant-auth"
    assert info["credential_source"] == "fabric_client_secret"
    assert info["configured_inputs"]["fabric_client_secret"] is True
    assert "super-secret-value" not in payload
