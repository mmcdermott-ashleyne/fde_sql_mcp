from __future__ import annotations

from contextlib import contextmanager
from typing import Optional

import pyodbc

from ..config import settings

_FABRIC_BROWSER_AUTH_MODES = {"browser", "default_browser"}


def _resolve_driver(preferred: Optional[str]) -> str:
    installed = {d.lower(): d for d in pyodbc.drivers()}
    if preferred:
        key = preferred.strip("{}").lower()
        if key in installed:
            return "{" + installed[key] + "}"

    fallback = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "SQL Server",
    ]
    for name in fallback:
        if name.lower() in installed:
            return "{" + installed[name.lower()] + "}"

    raise RuntimeError(
        "No SQL Server ODBC driver found. Install ODBC Driver 17 or 18."
    )


class SQLServerConnection:
    """
    SQL connector supporting on-prem Windows auth and Fabric Entra auth modes.
    """

    def __init__(
        self,
        server: str,
        database: str,
        driver: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        environment: str = "onprem",
    ) -> None:
        self.server = server
        self.database = database
        self.driver = driver or _resolve_driver(settings.sql_driver)
        self.username = username
        self.password = password
        self.environment = (environment or "onprem").strip().lower()

    def _build_fabric_auth_parts(self) -> list[str]:
        if self.username and self.password:
            return [f"Uid={self.username}", f"Pwd={self.password}"]

        mode = (settings.fabric_auth_mode or "").strip().lower()
        if mode == "client_secret":
            client_id = (settings.fabric_client_id or "").strip()
            client_secret = (settings.fabric_client_secret or "").strip()
            if not client_id or not client_secret:
                raise RuntimeError(
                    "Fabric auth mode is `client_secret`, but client credentials "
                    "are not fully configured."
                )
            return [
                "Authentication=ActiveDirectoryServicePrincipal",
                f"Uid={client_id}",
                f"Pwd={client_secret}",
            ]

        if mode in _FABRIC_BROWSER_AUTH_MODES:
            # Let the ODBC driver invoke interactive browser/device auth
            # when no cached Fabric token/session is available.
            return ["Authentication=ActiveDirectoryInteractive"]

        raise RuntimeError(
            "Unsupported Fabric auth mode "
            f"`{settings.fabric_auth_mode}`. "
            "Use `default_browser`, `browser`, or configure client-secret auth."
        )

    def _build_conn_str(self) -> str:
        server = self.server
        if settings.sql_server_port:
            server = f"{server},{settings.sql_server_port}"

        parts = [
            f"Driver={self.driver}",
            f"Server={server}",
            f"Database={self.database}",
            f"Encrypt={'yes' if settings.sql_encrypt else 'no'}",
            (
                "TrustServerCertificate=yes"
                if settings.sql_trust_server_certificate
                else "TrustServerCertificate=no"
            ),
            f"Connection Timeout={settings.sql_connection_timeout}",
            "Application Name=FDE SQL MCP",
        ]
        if self.environment == "fabric":
            parts.extend(self._build_fabric_auth_parts())
        elif self.username and self.password:
            parts.append(f"Uid={self.username}")
            parts.append(f"Pwd={self.password}")
        else:
            parts.append("Trusted_Connection=yes")
        if settings.sql_application_intent:
            parts.append(f"ApplicationIntent={settings.sql_application_intent}")
        return ";".join(parts) + ";"

    def _conn_open(self) -> pyodbc.Connection:
        conn_str = self._build_conn_str()
        return pyodbc.connect(conn_str)

    @contextmanager
    def get_connection(self):
        conn = self._conn_open()
        try:
            yield conn
        finally:
            try:
                conn.close()
            except Exception:
                pass


def get_sql_connection(
    *,
    server: str,
    database: str,
    username: str | None = None,
    password: str | None = None,
    environment: str = "onprem",
) -> SQLServerConnection:
    return SQLServerConnection(
        server=server,
        database=database,
        username=username,
        password=password,
        environment=environment,
    )
