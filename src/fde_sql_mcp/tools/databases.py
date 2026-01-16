from __future__ import annotations

from typing import Any, Dict, List, Sequence

from ..clients.sql import get_sql_connection
from ..config import settings


def _fetch_rows(
    database: str, query: str, params: Sequence[Any] | None = None
) -> List[Dict[str, Any]]:
    """Run the provided query against *database* and return rows as dicts."""
    conn = get_sql_connection(
        server=settings.sql_server,
        database=database,
    )
    with conn.get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def list_databases_impl() -> List[Dict[str, Any]]:
    """List every database visible to the configured server user."""
    return _fetch_rows(
        settings.sql_database,
        (
            "SELECT name, database_id, state_desc, recovery_model_desc "
            "FROM sys.databases "
            "ORDER BY name"
        ),
    )


def list_tables_impl(database: str) -> List[Dict[str, Any]]:
    """Return tables in *database*, one row per table with timestamps."""
    return _fetch_rows(
        database,
        (
            "SELECT s.name AS schema_name, t.name AS table_name, "
            "t.create_date, t.modify_date, t.is_ms_shipped, t.temporal_type_desc "
            "FROM sys.tables t "
            "JOIN sys.schemas s ON t.schema_id = s.schema_id "
            "ORDER BY s.name, t.name"
        ),
    )


def list_views_impl(database: str) -> List[Dict[str, Any]]:
    """Return views in *database* along with creation metadata."""
    return _fetch_rows(
        database,
        (
            "SELECT s.name AS schema_name, v.name AS view_name, "
            "v.create_date, v.modify_date, v.is_ms_shipped "
            "FROM sys.views v "
            "JOIN sys.schemas s ON v.schema_id = s.schema_id "
            "ORDER BY s.name, v.name"
        ),
    )


def list_stored_procedures_impl(database: str) -> List[Dict[str, Any]]:
    """Return stored procedures in *database* with type descriptions."""
    return _fetch_rows(
        database,
        (
            "SELECT s.name AS schema_name, p.name AS procedure_name, "
            "p.create_date, p.modify_date, p.is_ms_shipped, p.type_desc "
            "FROM sys.procedures p "
            "JOIN sys.schemas s ON p.schema_id = s.schema_id "
            "ORDER BY s.name, p.name"
        ),
    )


def list_indexes_impl(database: str) -> List[Dict[str, Any]]:
    """Return indexes scoped to tables in *database*."""
    return _fetch_rows(
        database,
        (
            "SELECT s.name AS schema_name, t.name AS table_name, i.name AS index_name, "
            "i.type_desc, i.is_unique, i.is_primary_key, i.is_disabled, i.fill_factor "
            "FROM sys.indexes i "
            "JOIN sys.tables t ON i.object_id = t.object_id "
            "JOIN sys.schemas s ON t.schema_id = s.schema_id "
            "WHERE i.name IS NOT NULL "
            "ORDER BY s.name, t.name, i.name"
        ),
    )
