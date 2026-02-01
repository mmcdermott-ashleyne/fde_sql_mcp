from __future__ import annotations

import re
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
        cursor.timeout = settings.sql_query_timeout
        cursor.execute(query, params or ())
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


_DISALLOWED_KEYWORDS = {
    "add",
    "alter",
    "backup",
    "begin",
    "bulk",
    "commit",
    "create",
    "delete",
    "deny",
    "drop",
    "exec",
    "execute",
    "grant",
    "insert",
    "into",
    "merge",
    "openquery",
    "openrowset",
    "opendatasource",
    "reconfigure",
    "restore",
    "revoke",
    "rollback",
    "save",
    "set",
    "shutdown",
    "truncate",
    "update",
    "use",
    "dbcc",
}


def _strip_sql_comments_and_literals(sql: str) -> str:
    without_block_comments = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    without_line_comments = re.sub(r"--[^\r\n]*", " ", without_block_comments)
    without_strings = re.sub(
        r"(?is)N?'(?:''|[^'])*'", " ", without_line_comments
    )
    without_brackets = re.sub(r"\[[^\]]*\]", " ", without_strings)
    return without_brackets


def _validate_readonly_query(query: str) -> None:
    if not settings.sql_enforce_readonly:
        return

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if len(query) > settings.sql_max_query_chars:
        raise ValueError(
            "Query exceeds the maximum allowed length for read-only execution."
        )

    stripped = _strip_sql_comments_and_literals(query)
    if not re.match(r"^\s*(with|select)\b", stripped, flags=re.I):
        raise ValueError(
            "Only SELECT statements (optionally starting with WITH) "
            "are allowed in read-only mode."
        )

    stripped_no_ws = stripped.strip()
    if ";" in stripped_no_ws[:-1]:
        raise ValueError("Multiple statements are not allowed in read-only mode.")

    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", stripped)
    for token in tokens:
        lower = token.lower()
        if lower in _DISALLOWED_KEYWORDS:
            raise ValueError(
                f"Disallowed keyword detected in read-only mode: {token}"
            )
        if lower.startswith("xp_") or lower.startswith("sp_"):
            raise ValueError(
                "Executing procedures is not allowed in read-only mode."
            )


def _normalize_max_rows(max_rows: int | None) -> int:
    if max_rows is None:
        return settings.sql_max_rows
    try:
        value = int(max_rows)
    except (TypeError, ValueError):
        return settings.sql_max_rows
    if value <= 0:
        return settings.sql_max_rows
    return min(value, settings.sql_max_rows)


def run_readonly_query_impl(
    database: str, query: str, max_rows: int | None = None
) -> Dict[str, Any]:
    """Execute a validated, read-only query with row limits enforced."""
    _validate_readonly_query(query)
    conn = get_sql_connection(
        server=settings.sql_server,
        database=database,
    )
    limit = _normalize_max_rows(max_rows)
    with conn.get_connection() as connection:
        cursor = connection.cursor()
        cursor.timeout = settings.sql_query_timeout
        cursor.execute(f"SET NOCOUNT ON; SET ROWCOUNT {limit}; {query}")
        columns = [column[0] for column in cursor.description or []]
        rows = cursor.fetchall()
    return {
        "rows": [dict(zip(columns, row)) for row in rows],
        "row_count": len(rows),
        "row_limit": limit,
        "truncated": len(rows) >= limit,
    }


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


def list_table_columns_impl(
    database: str, schema: str, table: str
) -> List[Dict[str, Any]]:
    """Return column metadata for the specified table."""
    return _fetch_rows(
        database,
        (
            "SELECT c.column_id, c.name AS column_name, t.name AS data_type, "
            "c.max_length, c.precision, c.scale, c.is_nullable, "
            "c.is_identity, c.is_computed, c.is_rowguidcol, "
            "c.collation_name, dc.definition AS default_definition "
            "FROM sys.columns c "
            "JOIN sys.tables tbl ON c.object_id = tbl.object_id "
            "JOIN sys.schemas s ON tbl.schema_id = s.schema_id "
            "JOIN sys.types t ON c.user_type_id = t.user_type_id "
            "LEFT JOIN sys.default_constraints dc "
            "ON c.default_object_id = dc.object_id "
            "WHERE s.name = ? AND tbl.name = ? "
            "ORDER BY c.column_id"
        ),
        (schema, table),
    )


def list_view_columns_impl(
    database: str, schema: str, view: str
) -> List[Dict[str, Any]]:
    """Return column metadata for the specified view."""
    return _fetch_rows(
        database,
        (
            "SELECT c.column_id, c.name AS column_name, t.name AS data_type, "
            "c.max_length, c.precision, c.scale, c.is_nullable, "
            "c.collation_name "
            "FROM sys.columns c "
            "JOIN sys.views v ON c.object_id = v.object_id "
            "JOIN sys.schemas s ON v.schema_id = s.schema_id "
            "JOIN sys.types t ON c.user_type_id = t.user_type_id "
            "WHERE s.name = ? AND v.name = ? "
            "ORDER BY c.column_id"
        ),
        (schema, view),
    )


def list_table_constraints_impl(
    database: str, schema: str, table: str
) -> List[Dict[str, Any]]:
    """Return primary key and unique constraints for the specified table."""
    return _fetch_rows(
        database,
        (
            "SELECT kc.name AS constraint_name, kc.type_desc, "
            "col.name AS column_name, ic.key_ordinal "
            "FROM sys.key_constraints kc "
            "JOIN sys.tables t ON kc.parent_object_id = t.object_id "
            "JOIN sys.schemas s ON t.schema_id = s.schema_id "
            "JOIN sys.index_columns ic "
            "ON kc.parent_object_id = ic.object_id "
            "AND kc.unique_index_id = ic.index_id "
            "JOIN sys.columns col "
            "ON ic.object_id = col.object_id "
            "AND ic.column_id = col.column_id "
            "WHERE s.name = ? AND t.name = ? "
            "ORDER BY kc.name, ic.key_ordinal"
        ),
        (schema, table),
    )


def list_foreign_keys_impl(
    database: str, schema: str, table: str
) -> List[Dict[str, Any]]:
    """Return foreign keys for the specified table."""
    return _fetch_rows(
        database,
        (
            "SELECT fk.name AS foreign_key_name, "
            "ps.name AS parent_schema, pt.name AS parent_table, "
            "pc.name AS parent_column, "
            "rs.name AS referenced_schema, rt.name AS referenced_table, "
            "rc.name AS referenced_column, "
            "fk.delete_referential_action_desc, "
            "fk.update_referential_action_desc, "
            "fk.is_disabled, fk.is_not_trusted, "
            "fkc.constraint_column_id "
            "FROM sys.foreign_keys fk "
            "JOIN sys.foreign_key_columns fkc "
            "ON fk.object_id = fkc.constraint_object_id "
            "JOIN sys.tables pt ON fkc.parent_object_id = pt.object_id "
            "JOIN sys.schemas ps ON pt.schema_id = ps.schema_id "
            "JOIN sys.columns pc "
            "ON pc.object_id = pt.object_id AND pc.column_id = fkc.parent_column_id "
            "JOIN sys.tables rt ON fkc.referenced_object_id = rt.object_id "
            "JOIN sys.schemas rs ON rt.schema_id = rs.schema_id "
            "JOIN sys.columns rc "
            "ON rc.object_id = rt.object_id AND rc.column_id = fkc.referenced_column_id "
            "WHERE ps.name = ? AND pt.name = ? "
            "ORDER BY fk.name, fkc.constraint_column_id"
        ),
        (schema, table),
    )


def list_index_details_impl(
    database: str, schema: str, table: str
) -> List[Dict[str, Any]]:
    """Return index definitions (including columns) for the specified table."""
    return _fetch_rows(
        database,
        (
            "SELECT i.name AS index_name, i.type_desc, i.is_unique, "
            "i.is_primary_key, i.is_unique_constraint, i.is_disabled, "
            "i.fill_factor, i.filter_definition, "
            "c.name AS column_name, ic.key_ordinal, ic.is_included_column, "
            "ic.is_descending_key "
            "FROM sys.indexes i "
            "JOIN sys.tables t ON i.object_id = t.object_id "
            "JOIN sys.schemas s ON t.schema_id = s.schema_id "
            "JOIN sys.index_columns ic "
            "ON i.object_id = ic.object_id AND i.index_id = ic.index_id "
            "JOIN sys.columns c "
            "ON ic.object_id = c.object_id AND ic.column_id = c.column_id "
            "WHERE s.name = ? AND t.name = ? AND i.name IS NOT NULL "
            "ORDER BY i.name, ic.key_ordinal, ic.index_column_id"
        ),
        (schema, table),
    )


def list_view_definition_impl(
    database: str, schema: str, view: str
) -> List[Dict[str, Any]]:
    """Return the SQL definition of the specified view."""
    return _fetch_rows(
        database,
        (
            "SELECT m.definition "
            "FROM sys.views v "
            "JOIN sys.schemas s ON v.schema_id = s.schema_id "
            "JOIN sys.sql_modules m ON v.object_id = m.object_id "
            "WHERE s.name = ? AND v.name = ?"
        ),
        (schema, view),
    )


def list_stored_procedure_definition_impl(
    database: str, schema: str, procedure: str
) -> List[Dict[str, Any]]:
    """Return the SQL definition of the specified stored procedure."""
    return _fetch_rows(
        database,
        (
            "SELECT m.definition "
            "FROM sys.procedures p "
            "JOIN sys.schemas s ON p.schema_id = s.schema_id "
            "JOIN sys.sql_modules m ON p.object_id = m.object_id "
            "WHERE s.name = ? AND p.name = ?"
        ),
        (schema, procedure),
    )


def list_stored_procedure_parameters_impl(
    database: str, schema: str, procedure: str
) -> List[Dict[str, Any]]:
    """Return parameters for the specified stored procedure."""
    return _fetch_rows(
        database,
        (
            "SELECT prm.name AS parameter_name, "
            "t.name AS data_type, prm.max_length, prm.precision, prm.scale, "
            "prm.is_output, prm.has_default_value "
            "FROM sys.procedures p "
            "JOIN sys.schemas s ON p.schema_id = s.schema_id "
            "JOIN sys.parameters prm ON p.object_id = prm.object_id "
            "JOIN sys.types t ON prm.user_type_id = t.user_type_id "
            "WHERE s.name = ? AND p.name = ? "
            "ORDER BY prm.parameter_id"
        ),
        (schema, procedure),
    )


def list_object_dependencies_impl(
    database: str, schema: str, object_name: str
) -> List[Dict[str, Any]]:
    """Return referenced objects for the specified object."""
    return _fetch_rows(
        database,
        (
            "SELECT d.referenced_server_name, d.referenced_database_name, "
            "d.referenced_schema_name, d.referenced_entity_name, "
            "d.referenced_id, d.is_ambiguous "
            "FROM sys.sql_expression_dependencies d "
            "JOIN sys.objects o ON d.referencing_id = o.object_id "
            "JOIN sys.schemas s ON o.schema_id = s.schema_id "
            "WHERE s.name = ? AND o.name = ? "
            "ORDER BY d.referenced_schema_name, d.referenced_entity_name"
        ),
        (schema, object_name),
    )
