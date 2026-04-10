from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

CONFIG_FILE_NAME = "fde_sql_mcp.config.json"
# config file lives at repository root, not inside src/
_CONFIG_PATH = Path(__file__).resolve().parents[2] / CONFIG_FILE_NAME


def _load_local_settings() -> dict[str, object]:
    try:
        raw = _CONFIG_PATH.read_text()
    except FileNotFoundError:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"{CONFIG_FILE_NAME} is invalid JSON: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{CONFIG_FILE_NAME} must contain a JSON object.")
    return data


_LOCAL_SETTINGS = _load_local_settings()


def _strip_or_none(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _local_setting(name: str) -> str | None:
    return _strip_or_none(_LOCAL_SETTINGS.get(name))


def _local_setting_raw(name: str) -> object | None:
    return _LOCAL_SETTINGS.get(name)


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def _get_sql_server() -> str:
    if server := _local_setting("sql_server"):
        return server
    if env := os.getenv("SQL_SERVER_HOST"):
        return env
    raise RuntimeError(
        "SQL_SERVER_HOST must be configured via an environment variable "
        f"or {CONFIG_FILE_NAME} before starting the server."
    )


def _get_sql_server_port() -> str | None:
    if port := _local_setting("sql_server_port"):
        return port
    return os.getenv("SQL_SERVER_PORT")


def _get_sql_database() -> str:
    return (
        _local_setting("sql_database")
        or os.getenv("SQL_SERVER_DATABASE", "master")
    )


def _get_sql_driver() -> str:
    return (
        _local_setting("sql_driver")
        or os.getenv("SQL_DRIVER", "{ODBC Driver 17 for SQL Server}")
    )


def _normalize_application_intent(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.lower() in {"readonly", "read-only", "read_only"}:
        return "ReadOnly"
    if normalized.lower() in {"readwrite", "read-write", "read_write"}:
        return "ReadWrite"
    return normalized


def _get_sql_application_intent() -> str | None:
    if intent := _local_setting("sql_application_intent"):
        return _normalize_application_intent(intent)
    if env := os.getenv("SQL_APPLICATION_INTENT"):
        return _normalize_application_intent(env)
    return "ReadOnly"


def _get_bool(local_name: str, env_name: str, default: bool) -> bool:
    value = _LOCAL_SETTINGS.get(local_name)
    if value is None:
        return _env_bool(env_name, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int(local_name: str, env_name: str, default: int) -> int:
    value = _LOCAL_SETTINGS.get(local_name)
    if value is None:
        return _env_int(env_name, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return _env_int(env_name, default)


def _get_str(local_name: str, env_name: str) -> str | None:
    if local := _local_setting(local_name):
        return local
    if env := os.getenv(env_name):
        return _strip_or_none(env)
    return None


def _normalize_fabric_auth_mode(value: str | None) -> str:
    if not value:
        return "default_browser"
    normalized = value.strip().lower().replace("-", "_")
    if normalized in {"default", "default_auth", "default_browser"}:
        return "default_browser"
    if normalized in {"browser", "interactive", "browser_capable"}:
        return "browser"
    if normalized == "client_secret":
        return "client_secret"
    return normalized


def _split_csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    parts = [part.strip() for part in value.split(",")]
    return tuple(part for part in parts if part)


def _normalize_string_list(
    value: object | None,
) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return _split_csv(value)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        normalized: list[str] = []
        for item in value:
            text = _strip_or_none(item)
            if text:
                normalized.append(text)
        return tuple(normalized)
    text = _strip_or_none(value)
    return (text,) if text else ()


def _get_string_list(local_name: str, env_name: str) -> tuple[str, ...]:
    raw = _local_setting_raw(local_name)
    if raw is not None:
        values = _normalize_string_list(raw)
        if values:
            return values
    return _split_csv(os.getenv(env_name))


def _normalize_string_mapping(value: object | None) -> dict[str, str]:
    if value is None:
        return {}

    if isinstance(value, dict):
        normalized: dict[str, str] = {}
        for key, mapped in value.items():
            src = _strip_or_none(key)
            dst = _strip_or_none(mapped)
            if src and dst:
                normalized[src] = dst
        return normalized

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            return _normalize_string_mapping(parsed)

        normalized: dict[str, str] = {}
        for pair in raw.split(","):
            if ":" not in pair:
                continue
            left, right = pair.split(":", 1)
            src = _strip_or_none(left)
            dst = _strip_or_none(right)
            if src and dst:
                normalized[src] = dst
        return normalized

    return {}


def _normalize_fabric_sql_endpoint_map(
    value: object | None,
) -> dict[str, dict[str, dict[str, str]]]:
    if value is None:
        return {}

    parsed: object = value
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {}

    if not isinstance(parsed, dict):
        return {}

    normalized: dict[str, dict[str, dict[str, str]]] = {}
    for workspace_key, endpoint_map in parsed.items():
        workspace = _strip_or_none(workspace_key)
        if not workspace or not isinstance(endpoint_map, dict):
            continue

        endpoint_entries: dict[str, dict[str, str]] = {}
        for endpoint_key, endpoint_value in endpoint_map.items():
            endpoint = _strip_or_none(endpoint_key)
            if not endpoint or not isinstance(endpoint_value, dict):
                continue

            endpoint_name = endpoint.lower()
            if endpoint_name not in {"warehouse", "lakehouse"}:
                continue

            server = _strip_or_none(endpoint_value.get("server"))
            database = _strip_or_none(endpoint_value.get("database"))
            if not server or not database:
                continue

            normalized_endpoint: dict[str, str] = {
                "server": server,
                "database": database,
            }
            user = _strip_or_none(endpoint_value.get("user"))
            password = _strip_or_none(endpoint_value.get("password"))
            if user:
                normalized_endpoint["user"] = user
            if password:
                normalized_endpoint["password"] = password

            endpoint_entries[endpoint_name] = normalized_endpoint

        if endpoint_entries:
            normalized[workspace.lower()] = endpoint_entries

    return normalized


def _get_string_mapping(local_name: str, env_name: str) -> dict[str, str]:
    raw = _local_setting_raw(local_name)
    if raw is not None:
        return _normalize_string_mapping(raw)
    return _normalize_string_mapping(os.getenv(env_name))


def _get_fabric_sql_endpoint_map(
    local_name: str, env_name: str
) -> dict[str, dict[str, dict[str, str]]]:
    raw = _local_setting_raw(local_name)
    if raw is not None:
        return _normalize_fabric_sql_endpoint_map(raw)
    return _normalize_fabric_sql_endpoint_map(os.getenv(env_name))


def _resolve_fabric_auth_mode(
    tenant_id: str | None,
    client_id: str | None,
    client_secret: str | None,
    fallback_mode: str,
) -> str:
    if tenant_id and client_id and client_secret:
        return "client_secret"
    return fallback_mode


@dataclass(frozen=True)
class Settings:
    """
    Package-wide configuration loaded from the local config file and environment.
    """

    sql_server: str = field(default_factory=_get_sql_server)
    sql_server_port: str | None = field(default_factory=_get_sql_server_port)
    sql_database: str = field(default_factory=_get_sql_database)
    sql_driver: str = field(default_factory=_get_sql_driver)
    sql_application_intent: str | None = field(
        default_factory=_get_sql_application_intent
    )
    sql_encrypt: bool = field(
        default_factory=lambda: _get_bool("sql_encrypt", "SQL_ENCRYPT", True)
    )
    sql_trust_server_certificate: bool = field(
        default_factory=lambda: _get_bool(
            "sql_trust_server_certificate", "SQL_TRUST_SERVER_CERTIFICATE", True
        )
    )
    sql_connection_timeout: int = field(
        default_factory=lambda: _get_int(
            "sql_connection_timeout", "SQL_CONNECTION_TIMEOUT", 30
        )
    )
    sql_query_timeout: int = field(
        default_factory=lambda: _get_int(
            "sql_query_timeout", "SQL_QUERY_TIMEOUT", 30
        )
    )
    sql_max_rows: int = field(
        default_factory=lambda: _get_int("sql_max_rows", "SQL_MAX_ROWS", 200)
    )
    sql_max_query_chars: int = field(
        default_factory=lambda: _get_int(
            "sql_max_query_chars", "SQL_MAX_QUERY_CHARS", 10000
        )
    )
    sql_enforce_readonly: bool = field(
        default_factory=lambda: _get_bool(
            "sql_enforce_readonly", "SQL_ENFORCE_READONLY", True
        )
    )
    fabric_enabled: bool = field(
        default_factory=lambda: _get_bool(
            "fabric_enabled", "FABRIC_ENABLED", False
        )
    )
    fabric_tenant_id: str | None = field(
        default_factory=lambda: _get_str("fabric_tenant_id", "FABRIC_TENANT_ID")
    )
    fabric_client_id: str | None = field(
        default_factory=lambda: _get_str("fabric_client_id", "FABRIC_CLIENT_ID")
    )
    fabric_client_secret: str | None = field(
        default_factory=lambda: _get_str(
            "fabric_client_secret", "FABRIC_CLIENT_SECRET"
        )
    )
    fabric_auth_fallback_mode: str = field(
        default_factory=lambda: _normalize_fabric_auth_mode(
            _get_str("fabric_auth_fallback_mode", "FABRIC_AUTH_FALLBACK_MODE")
        )
    )
    fabric_default_workspace: str | None = field(
        default_factory=lambda: _get_str(
            "fabric_default_workspace", "FABRIC_DEFAULT_WORKSPACE"
        )
    )
    fabric_default_database: str | None = field(
        default_factory=lambda: _get_str(
            "fabric_default_database", "FABRIC_DEFAULT_DATABASE"
        )
    )
    fabric_allowed_workspaces: tuple[str, ...] = field(
        default_factory=lambda: _get_string_list(
            "fabric_allowed_workspaces", "FABRIC_ALLOWED_WORKSPACES"
        )
    )
    fabric_allowed_databases: tuple[str, ...] = field(
        default_factory=lambda: _get_string_list(
            "fabric_allowed_databases", "FABRIC_ALLOWED_DATABASES"
        )
    )
    fabric_workspace_id_map: dict[str, str] = field(
        default_factory=lambda: _get_string_mapping(
            "fabric_workspace_id_map", "FABRIC_WORKSPACE_ID_MAP"
        )
    )
    fabric_sql_endpoint_map: dict[str, dict[str, dict[str, str]]] = field(
        default_factory=lambda: _get_fabric_sql_endpoint_map(
            "fabric_sql_endpoint_map", "FABRIC_SQL_ENDPOINT_MAP"
        )
    )
    fabric_auth_mode: str = field(init=False)
    fabric_tenant_context: str | None = field(init=False)

    def __post_init__(self) -> None:
        mode = _resolve_fabric_auth_mode(
            tenant_id=self.fabric_tenant_id,
            client_id=self.fabric_client_id,
            client_secret=self.fabric_client_secret,
            fallback_mode=self.fabric_auth_fallback_mode,
        )
        object.__setattr__(self, "fabric_auth_mode", mode)
        object.__setattr__(self, "fabric_tenant_context", self.fabric_tenant_id)


settings = Settings()
