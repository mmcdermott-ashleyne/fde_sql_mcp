from __future__ import annotations

from contextlib import contextmanager
from typing import Optional

import pyodbc

from ..config import settings


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
    Minimal SQL Server connector using Windows authentication.
    """

    def __init__(
        self,
        server: str,
        database: str,
        driver: Optional[str] = None,
    ) -> None:
        self.server = server
        self.database = database
        self.driver = driver or _resolve_driver(settings.sql_driver)

    def _build_conn_str(self) -> str:
        server = self.server
        if settings.sql_server_port:
            server = f"{server},{settings.sql_server_port}"

        parts = [
            f"Driver={self.driver}",
            f"Server={server}",
            f"Database={self.database}",
            "Trusted_Connection=yes",
            f"Encrypt={'yes' if settings.sql_encrypt else 'no'}",
            (
                "TrustServerCertificate=yes"
                if settings.sql_trust_server_certificate
                else "TrustServerCertificate=no"
            ),
            f"Connection Timeout={settings.sql_connection_timeout}",
            "Application Name=FDE SQL MCP",
        ]
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


def get_sql_connection(*, server: str, database: str) -> SQLServerConnection:
    return SQLServerConnection(server=server, database=database)
