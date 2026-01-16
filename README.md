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
  "sql_encrypt": true,
  "sql_trust_server_certificate": true,
  "sql_connection_timeout": 30
}
```

If the local file is missing, `SQL_SERVER_HOST` must be set in the environment (the other names below can still override the file values or work independently):

```text
SQL_SERVER_HOST=<required without local config>
SQL_SERVER_PORT=            # optional
SQL_SERVER_DATABASE=master
SQL_DRIVER={ODBC Driver 17 for SQL Server}
SQL_ENCRYPT=true
SQL_TRUST_SERVER_CERTIFICATE=true
SQL_CONNECTION_TIMEOUT=30
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

---

## Example Prompts

```text
List the databases on the SQL Server instance.

Show me the available SQL Server databases for my Windows login.
```
