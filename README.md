# FDE SQL MCP

An MCP server for on-prem SQL Server using Windows authentication. It starts with a single tool to list databases and provides a clean base to add more SQL tooling.

---

## Purpose

Use this server when you need MCP tooling to interact with an on-prem SQL Server instance via Windows auth (Trusted_Connection). It connects to the configured server and returns results as JSON for MCP clients.

---

## Features

- Simple stdio MCP server
- Windows-auth SQL Server connection (Trusted_Connection)
- Tools for listing databases, schema objects, and indexes per database

---

## Requirements

- Python 3.10+
- Access to the SQL Server host configured via `fde_sql_mcp.config.json` or `SQL_SERVER_HOST`
- Windows auth permissions for the account running the MCP server
- ODBC Driver 17 or 18 for SQL Server installed

---

## Installation

```bash
# create & activate a venv (required so Windows auth works predictably)
python -m venv .venv
.venv\Scripts\activate

# install the MCP client/programming helpers so the MCP runtime is available
pip install mcp

# install the project dependencies
pip install -r requirements.txt

# install this package in editable mode so imports work from the repo root
pip install -e .
```

---

## Configuration

Create a local `fde_sql_mcp.config.json` file at the repo root (copy `fde_sql_mcp.config.template.json`) and populate it with the actual SQL Server endpoint and any overrides. The template is committed, the working file is ignored, and the loader prefers the local file so the private IP never enters version control.

```json
{
  "sql_server": "your.sql.server.address",
  "sql_server_port": 1433,
  "sql_database": "master",
  "sql_driver": "{ODBC Driver 17 for SQL Server}",
  "sql_application_intent": "ReadOnly",
  "sql_encrypt": true,
  "sql_trust_server_certificate": true,
  "sql_connection_timeout": 30,
  "sql_query_timeout": 30,
  "sql_max_rows": 200,
  "sql_max_query_chars": 10000,
  "sql_enforce_readonly": true
}
```

If the local file is missing, `SQL_SERVER_HOST` must be set in the environment (the other names below can still override the file values or work independently):

```text
SQL_SERVER_HOST=<required without local config>
SQL_SERVER_PORT=            # optional
SQL_SERVER_DATABASE=master
SQL_DRIVER={ODBC Driver 17 for SQL Server}
SQL_APPLICATION_INTENT=ReadOnly
SQL_ENCRYPT=true
SQL_TRUST_SERVER_CERTIFICATE=true
SQL_CONNECTION_TIMEOUT=30
SQL_QUERY_TIMEOUT=30
SQL_MAX_ROWS=200
SQL_MAX_QUERY_CHARS=10000
SQL_ENFORCE_READONLY=true
```

Notes:
- Windows auth is always used (`Trusted_Connection=yes`).
- `SQL_TRUST_SERVER_CERTIFICATE=true` matches your trusted cert requirement.

---

## Running the MCP Server

```bash
python -m fde_sql_mcp.server
```

### Example MCP config snippet

```jsonc
{
  "name": "fde-sql-mcp",
  "command": ["python", "-m", "fde_sql_mcp.server"],
  "env": {
    "SQL_SERVER_HOST": "your.sql.server.address",
    "SQL_SERVER_DATABASE": "master",
    "SQL_ENCRYPT": "true",
    "SQL_TRUST_SERVER_CERTIFICATE": "true"
  }
}
```

---

## Tools

### `list_databases()`

Lists databases visible to the Windows-authenticated user.

Example response:

```json
[
  {
    "name": "master",
    "database_id": 1,
    "state_desc": "ONLINE",
    "recovery_model_desc": "SIMPLE"
  }
]
```

### `list_tables(database: str)`

Enumerates tables in the provided database with schema name, creation/modify timestamps, and temporal type metadata.

### `list_views(database: str)`

Enumerates views in the provided database along with schema and timestamps.

### `list_stored_procedures(database: str)`

Enumerates stored procedures in the provided database including creation metadata and whether the object is shipped with SQL Server.

### `list_indexes(database: str)`

Enumerates non-null index definitions scoped to tables in the provided database (includes uniqueness, primary key flag, disabled state, and fill factor).

### `run_readonly_query(database: str, query: str, max_rows: int | None)`

Executes a validated read-only query (SELECT/CTE only) with a server-side row cap. The response includes rows, row_count, row_limit, and a truncated flag.

### `list_table_columns(database: str, schema: str, table: str)`

Returns column-level metadata for a table (types, nullability, identity/computed flags, defaults, collation).

### `list_view_columns(database: str, schema: str, view: str)`

Returns column-level metadata for a view.

### `list_table_constraints(database: str, schema: str, table: str)`

Returns primary key and unique constraints for the specified table.

### `list_foreign_keys(database: str, schema: str, table: str)`

Returns foreign key relationships for the specified table (including actions and referenced columns).

### `list_index_details(database: str, schema: str, table: str)`

Returns detailed index definitions for the specified table, including key/include columns and filters.

### `list_view_definition(database: str, schema: str, view: str)`

Returns the SQL definition of the specified view.

### `list_stored_procedure_definition(database: str, schema: str, procedure: str)`

Returns the SQL definition of the specified stored procedure.

### `list_stored_procedure_parameters(database: str, schema: str, procedure: str)`

Returns parameter metadata for the specified stored procedure.

### `list_object_dependencies(database: str, schema: str, object_name: str)`

Returns referenced objects for a view or stored procedure based on `sys.sql_expression_dependencies`.

---

## Example Prompts

```text
List the databases on the SQL Server instance.

Show me the available SQL Server databases for my Windows login.
```
