# Architecture

**Analysis Date:** 2026-04-10

## Pattern Overview

**Overall:** Layered MCP server with thin async tool endpoints over synchronous SQL query implementations.

**Key Characteristics:**
- Tool registration and transport are centralized in `src/fde_sql_mcp/server.py`.
- Business/query logic is isolated in `src/fde_sql_mcp/tools/databases.py`.
- SQL connectivity and connection-string concerns are isolated in `src/fde_sql_mcp/clients/sql.py`.
- Configuration is resolved once through `src/fde_sql_mcp/config.py` and consumed across layers.

## Layers

**Transport Layer (MCP Server):**
- Purpose: Expose callable MCP tools and run stdio server lifecycle.
- Location: `src/fde_sql_mcp/server.py`.
- Contains: `FastMCP` instance, `@mcp.tool` async handlers, `run()` entrypoint.
- Depends on: `mcp.server.fastmcp.FastMCP`, `src/fde_sql_mcp/tools/databases.py`.
- Used by: MCP runtime via `python -m fde_sql_mcp.server` and `pyproject.toml` entrypoint `fde_sql_mcp.server:run`.

**Tool/Domain Layer (SQL Metadata + Query Operations):**
- Purpose: Implement read-only SQL operations and schema inspection queries.
- Location: `src/fde_sql_mcp/tools/databases.py`.
- Contains: `_fetch_rows`, read-only validator, and `*_impl` functions (`list_tables_impl`, `run_readonly_query_impl`, etc.).
- Depends on: `src/fde_sql_mcp/clients/sql.py`, `src/fde_sql_mcp/config.py`.
- Used by: `src/fde_sql_mcp/server.py` through `asyncio.to_thread(...)`.

**Data Access Layer (Connection Management):**
- Purpose: Resolve ODBC driver, build SQL Server connection string, and provide context-managed connections.
- Location: `src/fde_sql_mcp/clients/sql.py`.
- Contains: `_resolve_driver`, `SQLServerConnection`, `get_sql_connection`.
- Depends on: `pyodbc`, `src/fde_sql_mcp/config.py`.
- Used by: `src/fde_sql_mcp/tools/databases.py`.

**Configuration Layer:**
- Purpose: Merge local JSON config and environment overrides into immutable runtime settings.
- Location: `src/fde_sql_mcp/config.py`.
- Contains: local config loader, env parsers, `Settings` dataclass, singleton `settings`.
- Depends on: `fde_sql_mcp.config.json` (if present), environment variables.
- Used by: `src/fde_sql_mcp/tools/databases.py`, `src/fde_sql_mcp/clients/sql.py`.

## Data Flow

**MCP Tool Request Flow:**

1. Client invokes a registered MCP tool exposed in `src/fde_sql_mcp/server.py`.
2. Async handler delegates to implementation using `asyncio.to_thread(...)` in `src/fde_sql_mcp/server.py`.
3. Implementation in `src/fde_sql_mcp/tools/databases.py` validates input (for `run_readonly_query_impl`) and prepares SQL.
4. Query execution uses `get_sql_connection(...)` from `src/fde_sql_mcp/clients/sql.py`.
5. `SQLServerConnection.get_connection()` opens/closes pyodbc connection in `src/fde_sql_mcp/clients/sql.py`.
6. Result rows are converted to JSON-serializable dicts in `src/fde_sql_mcp/tools/databases.py`.
7. Response is returned through MCP JSON response mode configured in `src/fde_sql_mcp/server.py`.

**State Management:**
- Runtime is stateless per request; no in-memory cache is implemented in `src/fde_sql_mcp/tools/databases.py`.
- Shared process configuration state is immutable via `settings = Settings()` in `src/fde_sql_mcp/config.py`.

## Key Abstractions

**MCP Tool Surface (`FastMCP`):**
- Purpose: Define external tool contract and descriptions for clients.
- Examples: `ping`, `list_databases`, `run_readonly_query` in `src/fde_sql_mcp/server.py`.
- Pattern: Thin async wrappers that delegate all domain logic to `*_impl` functions.

**SQL Connection Abstraction (`SQLServerConnection`):**
- Purpose: Encapsulate connection-string creation and resource management.
- Examples: `SQLServerConnection._build_conn_str`, `SQLServerConnection.get_connection` in `src/fde_sql_mcp/clients/sql.py`.
- Pattern: Context manager boundary around each DB operation.

**Read-only Query Guard:**
- Purpose: Enforce safe read-only execution path.
- Examples: `_validate_readonly_query`, `_DISALLOWED_KEYWORDS` in `src/fde_sql_mcp/tools/databases.py`.
- Pattern: Pre-execution lexical checks plus max length/row limits from `src/fde_sql_mcp/config.py`.

## Entry Points

**CLI/Module Entrypoint:**
- Location: `src/fde_sql_mcp/server.py`.
- Triggers: `python -m fde_sql_mcp.server`.
- Responsibilities: initialize MCP server instance and call `mcp.run()` in `run()`.

**MCP Packaging Entrypoint:**
- Location: `pyproject.toml` (`[tool.mcp.entrypoints] default = "fde_sql_mcp.server:run"`).
- Triggers: MCP tooling that resolves configured project entrypoint.
- Responsibilities: expose default callable to launch server.

## Error Handling

**Strategy:** Fail fast on invalid configuration/input; propagate runtime DB errors to caller.

**Patterns:**
- Config validation raises `RuntimeError` for missing/invalid config in `src/fde_sql_mcp/config.py`.
- Query validation raises `ValueError` for non-read-only or malformed requests in `src/fde_sql_mcp/tools/databases.py`.
- Driver resolution raises `RuntimeError` when ODBC driver is missing in `src/fde_sql_mcp/clients/sql.py`.
- Connection close is best-effort via guarded `except Exception: pass` in `src/fde_sql_mcp/clients/sql.py`.

## Cross-Cutting Concerns

**Logging:** Minimal stderr startup log in `src/fde_sql_mcp/server.py`; no structured logging framework detected.
**Validation:** Central read-only SQL validation in `src/fde_sql_mcp/tools/databases.py`; config normalization in `src/fde_sql_mcp/config.py`.
**Authentication:** Windows integrated auth via `Trusted_Connection=yes` in `src/fde_sql_mcp/clients/sql.py`.

---

*Architecture analysis: 2026-04-10*
