# External Integrations

**Analysis Date:** 2026-04-10

## APIs & External Services

**Database Service:**
- Microsoft SQL Server - primary external system for schema metadata and read-only query execution.
  - SDK/Client: `pyodbc` in `src/fde_sql_mcp/clients/sql.py` (connection creation, driver selection, query execution).
  - Auth: Windows integrated auth (`Trusted_Connection=yes`) hardcoded in `src/fde_sql_mcp/clients/sql.py`.

**Protocol Surface:**
- MCP over stdio - this service exposes MCP tools to an MCP host/client process.
  - SDK/Client: `mcp.server.fastmcp.FastMCP` in `src/fde_sql_mcp/server.py`.
  - Auth: Not implemented in this repo; trust boundary is the invoking MCP host process (`src/fde_sql_mcp/server.py`).

## Data Storage

**Databases:**
- Microsoft SQL Server (external, configurable target).
  - Connection: `SQL_SERVER_HOST` (required fallback) plus optional vars from `src/fde_sql_mcp/config.py`.
  - Client: `pyodbc` wrapper class `SQLServerConnection` in `src/fde_sql_mcp/clients/sql.py`.

**File Storage:**
- Local filesystem only for configuration (`fde_sql_mcp.config.json` preferred, template in `fde_sql_mcp.config.template.json`, loading logic in `src/fde_sql_mcp/config.py`).

**Caching:**
- None detected in `src/fde_sql_mcp/`.

## Authentication & Identity

**Auth Provider:**
- Windows/SQL Server integrated security (OS identity passthrough).
  - Implementation: ODBC connection string uses `Trusted_Connection=yes`, optional TLS controls (`Encrypt`, `TrustServerCertificate`) in `src/fde_sql_mcp/clients/sql.py`, with values resolved from `src/fde_sql_mcp/config.py`.

## Monitoring & Observability

**Error Tracking:**
- None detected (no Sentry/Application Insights/OpenTelemetry packages in `pyproject.toml` or `requirements.txt`).

**Logs:**
- Minimal process logging to stderr on startup in `src/fde_sql_mcp/server.py`.
- No structured log sink integration detected in `src/fde_sql_mcp/`.

## CI/CD & Deployment

**Hosting:**
- Self-hosted process execution expected (`python -m fde_sql_mcp.server`) from `README.md`.

**CI Pipeline:**
- None detected (`.github/` not present, no CI YAML files detected at repository root excluding `.venv/`).

## Environment Configuration

**Required env vars:**
- `SQL_SERVER_HOST` (required if local config file is absent) in `src/fde_sql_mcp/config.py`.
- Operational env vars supported by `src/fde_sql_mcp/config.py` and documented in `README.md`:
- `SQL_SERVER_PORT`
- `SQL_SERVER_DATABASE`
- `SQL_DRIVER`
- `SQL_APPLICATION_INTENT`
- `SQL_ENCRYPT`
- `SQL_TRUST_SERVER_CERTIFICATE`
- `SQL_CONNECTION_TIMEOUT`
- `SQL_QUERY_TIMEOUT`
- `SQL_MAX_ROWS`
- `SQL_MAX_QUERY_CHARS`
- `SQL_ENFORCE_READONLY`

**Secrets location:**
- Local ignored config file `fde_sql_mcp.config.json` (ignored by `.gitignore`).
- Process environment variables at runtime (`src/fde_sql_mcp/config.py`).

## Webhooks & Callbacks

**Incoming:**
- None detected (no HTTP server/webhook routes in `src/fde_sql_mcp/`).

**Outgoing:**
- None detected (no webhook callback clients; outbound calls are SQL connections only in `src/fde_sql_mcp/clients/sql.py`).

---

*Integration audit: 2026-04-10*
