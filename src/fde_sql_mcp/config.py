from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

CONFIG_FILE_NAME = "fde_sql_mcp.config.json"
_CONFIG_PATH = Path(__file__).resolve().parents[1] / CONFIG_FILE_NAME


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


@dataclass(frozen=True)
class Settings:
    """
    Package-wide configuration loaded from the local config file and environment.
    """

    sql_server: str = field(default_factory=_get_sql_server)
    sql_server_port: str | None = field(default_factory=_get_sql_server_port)
    sql_database: str = field(default_factory=_get_sql_database)
    sql_driver: str = field(default_factory=_get_sql_driver)
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


settings = Settings()
