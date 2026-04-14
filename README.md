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
  "sql_enforce_readonly": true,
  "fabric_enabled": false,
  "fabric_tenant_id": "",
  "fabric_client_id": "",
  "fabric_client_secret": "",
  "fabric_auth_fallback_mode": "default_browser",
  "fabric_default_workspace": "",
  "fabric_default_database": "",
  "fabric_workspace_id_map": {
    "fde_core_data_dev": "",
    "fde_core_data_stg": "",
    "fde_core_data_prod": ""
  },
  "fabric_sql_endpoint_map": {
    "fde_core_data_dev": {
      "warehouse": {
        "server": "dev-warehouse.sql.fabric.microsoft.com",
        "database": "core_dw",
        "user": "",
        "password": ""
      },
      "lakehouse": {
        "server": "dev-lakehouse.sql.fabric.microsoft.com",
        "database": "core_lh",
        "user": "",
        "password": ""
      }
    }
  },
  "fabric_allowed_workspaces": ["fde_core_data_dev", "fde_core_data_stg", "fde_core_data_prod"],
  "fabric_allowed_databases": ["core_dw", "core_lh"]
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
FABRIC_ENABLED=false
FABRIC_TENANT_ID=
FABRIC_CLIENT_ID=
FABRIC_CLIENT_SECRET=
FABRIC_AUTH_FALLBACK_MODE=default_browser
FABRIC_DEFAULT_WORKSPACE=
FABRIC_DEFAULT_DATABASE=
FABRIC_WORKSPACE_ID_MAP=  # JSON object or comma pairs (workspace:id)
FABRIC_SQL_ENDPOINT_MAP=  # JSON object keyed by workspace with warehouse/lakehouse server+database (+ optional user/password)
FABRIC_ALLOWED_WORKSPACES=fde_core_data_dev,fde_core_data_stg,fde_core_data_prod
FABRIC_ALLOWED_DATABASES=core_dw,core_lh
```

Notes:
- On-prem SQL uses Windows auth (`Trusted_Connection=yes`).
- Fabric SQL endpoint auth is derived from `fabric_sql_endpoint_map`:
  - if `user` and `password` are provided, SQL auth is used;
  - if omitted, Windows auth is attempted (useful for dev/test environments with delegated access).
- `SQL_TRUST_SERVER_CERTIFICATE=true` matches your trusted cert requirement.
- Fabric auth mode precedence is deterministic:
  - `client_secret` mode when `FABRIC_TENANT_ID`, `FABRIC_CLIENT_ID`, and `FABRIC_CLIENT_SECRET` are all configured.
  - Fallback mode (`FABRIC_AUTH_FALLBACK_MODE`, default `default_browser`) when any client-secret value is missing.
- Fabric workspace routing can map canonical workspace names to IDs using `fabric_workspace_id_map` / `FABRIC_WORKSPACE_ID_MAP`.
- Fabric endpoint execution requires `fabric_sql_endpoint_map` / `FABRIC_SQL_ENDPOINT_MAP` entries for each allowlisted workspace + endpoint pair you route to.

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

## Operator Guide (On-Prem + Fabric)

### 1) Dual-Environment Setup Checklist

- Configure on-prem SQL defaults (`sql_server`, `sql_database`) in `fde_sql_mcp.config.json`.
- Configure Fabric allowlists:
  - `fabric_allowed_workspaces`: only `fde_core_data_dev`, `fde_core_data_stg`, `fde_core_data_prod`
  - `fabric_allowed_databases`: only `core_dw`, `core_lh`
- Configure endpoint map entries for every workspace/endpoint pair you plan to query:
  - `fabric_sql_endpoint_map.<workspace>.warehouse` -> `server` + `database=core_dw`
  - `fabric_sql_endpoint_map.<workspace>.lakehouse` -> `server` + `database=core_lh`
- Keep safety limits configured:
  - `sql_enforce_readonly=true`
  - `sql_max_rows`
  - `sql_max_query_chars`
  - `sql_query_timeout`

### 2) Fabric Auth Precedence

Auth mode is deterministic:
1. `client_secret` mode when all three variables are set:
   - `FABRIC_TENANT_ID`
   - `FABRIC_CLIENT_ID`
   - `FABRIC_CLIENT_SECRET`
2. Otherwise use fallback mode from `FABRIC_AUTH_FALLBACK_MODE` (default `default_browser`).

Use `get_auth_info()` to confirm the effective auth mode and configured input presence.

### 3) Route Selection Examples

Explicit target switching:

```text
set_query_target("onprem")
set_query_target("fabric workspace=fde_core_data_dev endpoint=warehouse database=core_dw")
set_query_target("fabric workspace=fde_core_data_prod endpoint=lakehouse database=core_lh")
```

Natural-language target selection:

```text
set_query_target("query fabric prod lakehouse")
set_query_target("run this in fabric dev warehouse")
```

Verify active route before querying:

```text
get_query_target()
```

### 4) Safety Guardrail Behavior

`run_readonly_query` guardrails are enforced consistently for both on-prem and Fabric targets:

- Non-read-only SQL is rejected:
  - Example: `DELETE FROM dbo.table_name`
  - Expected error: only `SELECT`/`WITH` statements are allowed.
- Oversized SQL is rejected:
  - Example: query text length exceeds `sql_max_query_chars`
  - Expected error: maximum read-only query length exceeded.
- Row requests above configured max are clamped:
  - Example: `max_rows=1000` with `sql_max_rows=200`
  - Expected behavior: `row_limit` returns `200`, `truncated` reflects capped results.
- Timeout applies to SQL execution cursors for query and metadata operations:
  - Source: `sql_query_timeout`

If a query fails, check whether the error is:
- **Routing/governance** (workspace/database mismatch, missing endpoint mapping), or
- **Safety validation** (read-only/size/row-limit guardrail).

---

## Tools

### `get_auth_info()`

Returns non-secret Fabric authentication diagnostics:
- resolved auth mode (`client_secret`, `default_browser`, or configured fallback),
- credential source,
- resolved tenant context,
- booleans indicating which Fabric auth inputs are configured.

### `set_query_target(target: str)`

Sets the active routing target for query execution using explicit or natural-language hints.

Examples:
- `onprem`
- `fabric workspace=fde_core_data_dev endpoint=warehouse database=core_dw`
- `query fabric prod lakehouse`

### `get_query_target()`

Returns the currently active routing target context:
- environment,
- workspace/workspace_id (for Fabric),
- endpoint type,
- database.

### `list_fabric_workspaces()`

Lists only allowlisted Fabric workspaces and configured workspace ID mappings.
Out-of-allowlist workspaces are never returned.

### `list_databases()`

Lists databases visible to the currently routed SQL target.

Notes:
- On-prem target: uses configured SQL Server (`Trusted_Connection`).
- Fabric target: uses routed Fabric endpoint/database mapping from `fabric_sql_endpoint_map`.

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

Notes:
- For Fabric targets, `database` must match the routed target database (`core_dw` for warehouse, `core_lh` for lakehouse).

### `list_views(database: str)`

Enumerates views in the provided database along with schema and timestamps.

### `list_stored_procedures(database: str)`

Enumerates stored procedures in the provided database including creation metadata and whether the object is shipped with SQL Server.

### `list_indexes(database: str)`

Enumerates non-null index definitions scoped to tables in the provided database (includes uniqueness, primary key flag, disabled state, and fill factor).

### `run_readonly_query(database: str, query: str, max_rows: int | None)`

Executes a validated read-only query (SELECT/CTE only) with a server-side row cap. The response includes rows, row_count, row_limit, truncated flag, and `target_context`.

Notes:
- Active Fabric targets execute against configured Fabric SQL endpoint mappings while preserving the same read-only contract.
- `target_context` always reflects the resolved active routing target used for execution.

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
