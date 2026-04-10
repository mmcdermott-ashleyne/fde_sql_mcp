# Technology Stack

**Analysis Date:** 2026-04-10

## Languages

**Primary:**
- Python 3.10+ - MCP server implementation in `src/fde_sql_mcp/server.py`, configuration in `src/fde_sql_mcp/config.py`, SQL client logic in `src/fde_sql_mcp/clients/sql.py`, and tool handlers in `src/fde_sql_mcp/tools/databases.py`.

**Secondary:**
- SQL (T-SQL) - Metadata and query operations embedded as SQL statements in `src/fde_sql_mcp/tools/databases.py`.
- JSON - Runtime configuration schema in `fde_sql_mcp.config.template.json` and loader logic in `src/fde_sql_mcp/config.py`.

## Runtime

**Environment:**
- Python runtime >=3.10 required by `pyproject.toml` (`requires-python = ">=3.10"`).
- Virtual environment workflow documented in `README.md` (`python -m venv .venv`).

**Package Manager:**
- `pip` with dependency install flow in `README.md` (`pip install -r requirements.txt`, `pip install -e .`).
- Lockfile: missing (`poetry.lock`, `Pipfile.lock`, `uv.lock` not detected at repository root).

## Frameworks

**Core:**
- MCP Python SDK (`mcp[cli]`) - FastMCP server runtime and tool registration (`src/fde_sql_mcp/server.py`, `pyproject.toml`, `requirements.txt`).

**Testing:**
- `pytest` (dev optional dependency) - declared under `[project.optional-dependencies]` in `pyproject.toml`.

**Build/Dev:**
- `ruff` (dev optional dependency) - declared under `[project.optional-dependencies]` in `pyproject.toml`.
- Editable package entrypoint through `[tool.mcp.entrypoints]` in `pyproject.toml` (`fde_sql_mcp.server:run`).

## Key Dependencies

**Critical:**
- `mcp[cli]` - provides `FastMCP` server class used in `src/fde_sql_mcp/server.py`.
- `pyodbc` - SQL Server ODBC connectivity and driver discovery in `src/fde_sql_mcp/clients/sql.py`.

**Infrastructure:**
- ODBC Driver 17 or 18 for SQL Server (system dependency) - required in `README.md` and fallback/validation logic in `src/fde_sql_mcp/clients/sql.py`.

## Configuration

**Environment:**
- Configuration sources are layered local JSON then environment variables in `src/fde_sql_mcp/config.py`.
- Root config filename is fixed as `fde_sql_mcp.config.json` in `src/fde_sql_mcp/config.py` and ignored in `.gitignore`.
- Required without local config: `SQL_SERVER_HOST` (enforced in `src/fde_sql_mcp/config.py`).
- Additional supported env vars are documented in `README.md` and resolved in `src/fde_sql_mcp/config.py`: `SQL_SERVER_PORT`, `SQL_SERVER_DATABASE`, `SQL_DRIVER`, `SQL_APPLICATION_INTENT`, `SQL_ENCRYPT`, `SQL_TRUST_SERVER_CERTIFICATE`, `SQL_CONNECTION_TIMEOUT`, `SQL_QUERY_TIMEOUT`, `SQL_MAX_ROWS`, `SQL_MAX_QUERY_CHARS`, `SQL_ENFORCE_READONLY`.

**Build:**
- Project metadata and MCP entrypoint config in `pyproject.toml`.
- Default runtime config schema in `fde_sql_mcp.config.template.json`.

## Platform Requirements

**Development:**
- Windows-authenticated connectivity to SQL Server (`Trusted_Connection=yes`) in `src/fde_sql_mcp/clients/sql.py`.
- SQL Server access and ODBC installation prerequisites documented in `README.md`.
- Local Python environment expected at `.venv/` (present in repository root listing and documented in `README.md`).

**Production:**
- Deployment target is an MCP stdio process (`python -m fde_sql_mcp.server`) described in `README.md` and implemented in `src/fde_sql_mcp/server.py`.
- Back-end dependency is on-prem or reachable Microsoft SQL Server instance configured by `fde_sql_mcp.config.json` or `SQL_SERVER_HOST` (`src/fde_sql_mcp/config.py`).

---

*Stack analysis: 2026-04-10*
