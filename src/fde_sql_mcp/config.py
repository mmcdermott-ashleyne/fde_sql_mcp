from __future__ import annotations

import os
from dataclasses import dataclass


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


@dataclass(frozen=True)
class Settings:
    """
    Package-wide configuration loaded from environment variables.
    """

    sql_server: str = os.getenv("SQL_SERVER_HOST", "10.91.24.20")
    sql_server_port: str | None = os.getenv("SQL_SERVER_PORT")
    sql_database: str = os.getenv("SQL_SERVER_DATABASE", "master")
    sql_driver: str = os.getenv("SQL_DRIVER", "{ODBC Driver 17 for SQL Server}")
    sql_encrypt: bool = _env_bool("SQL_ENCRYPT", True)
    sql_trust_server_certificate: bool = _env_bool(
        "SQL_TRUST_SERVER_CERTIFICATE", True
    )
    sql_connection_timeout: int = _env_int("SQL_CONNECTION_TIMEOUT", 30)


settings = Settings()
