# Coding Conventions

**Analysis Date:** 2026-04-10

## Naming Patterns

**Files:**
- Use `snake_case.py` module names for implementation files (examples: `src/fde_sql_mcp/config.py`, `src/fde_sql_mcp/server.py`, `src/fde_sql_mcp/tools/databases.py`, `src/fde_sql_mcp/clients/sql.py`).
- Keep package sentinel names standard (`src/fde_sql_mcp/__init__.py`).

**Functions:**
- Use `snake_case` for all functions, including MCP handlers and internal helpers (examples: `list_databases`, `run_readonly_query`, `_validate_readonly_query` in `src/fde_sql_mcp/server.py` and `src/fde_sql_mcp/tools/databases.py`).
- Prefix internal helpers with a leading underscore (examples: `_load_local_settings`, `_get_int` in `src/fde_sql_mcp/config.py`).

**Variables:**
- Use `snake_case` for local variables and parameters (examples: `max_rows`, `sql_application_intent` across `src/fde_sql_mcp/config.py` and `src/fde_sql_mcp/tools/databases.py`).
- Use `UPPER_SNAKE_CASE` for module constants (examples: `CONFIG_FILE_NAME`, `_CONFIG_PATH`, `_LOCAL_SETTINGS`, `_DISALLOWED_KEYWORDS`).

**Types:**
- Use `PascalCase` for classes/dataclasses (examples: `Settings`, `SQLServerConnection`).
- Use built-in generic annotations and union syntax (`dict[str, object]`, `str | None`) as seen in `src/fde_sql_mcp/config.py`.

## Code Style

**Formatting:**
- Tool used: Not enforced by checked-in formatter config.
- Key settings: No `.prettierrc*`, `black`, or `ruff` config block detected; style follows PEP 8-like spacing and line wrapping in `src/fde_sql_mcp/*.py`.

**Linting:**
- Tool used: `ruff` is declared only as a dev optional dependency in `pyproject.toml`.
- Key rules: Not detected (`[tool.ruff]` section not present in `pyproject.toml`).

## Import Organization

**Order:**
1. `from __future__ import annotations` first (`src/fde_sql_mcp/config.py`, `src/fde_sql_mcp/server.py`, `src/fde_sql_mcp/tools/databases.py`, `src/fde_sql_mcp/clients/sql.py`)
2. Standard library imports (`json`, `os`, `asyncio`, `re`, `typing`)
3. Third-party imports (`pyodbc`, `mcp.server.fastmcp`)
4. Local relative imports (`from ..config import settings`, `from .tools import databases as DB`)

**Path Aliases:**
- Not used; imports are package-relative (`src/fde_sql_mcp/server.py`, `src/fde_sql_mcp/tools/databases.py`).

## Error Handling

**Patterns:**
- Raise `RuntimeError` for invalid startup/config/driver states (`src/fde_sql_mcp/config.py`, `src/fde_sql_mcp/clients/sql.py`).
- Raise `ValueError` for invalid runtime query input (`src/fde_sql_mcp/tools/databases.py`).
- Use defensive `try/except` for optional runtime behavior (`cursor.timeout`) and best-effort cleanup (`conn.close()`) in `src/fde_sql_mcp/tools/databases.py` and `src/fde_sql_mcp/clients/sql.py`.

## Logging

**Framework:** `print` to `stderr`

**Patterns:**
- Emit startup status once in `run()` (`src/fde_sql_mcp/server.py`).
- Avoid verbose logging in query/config paths; errors are surfaced via exceptions.

## Comments

**When to Comment:**
- Use section banner comments to separate server concerns (`src/fde_sql_mcp/server.py`).
- Add short rationale comments for compatibility edge cases (pyodbc timeout support in `src/fde_sql_mcp/tools/databases.py`).

**JSDoc/TSDoc:**
- Not applicable (Python codebase). Use concise Python docstrings on public helpers/impl functions (`src/fde_sql_mcp/tools/databases.py`, `src/fde_sql_mcp/config.py`).

## Function Design

**Size:** Favor small focused functions; MCP handlers in `src/fde_sql_mcp/server.py` are thin wrappers over `*_impl` functions.

**Parameters:** Use explicit typed parameters for database/schema/object names (examples in `src/fde_sql_mcp/tools/databases.py`).

**Return Values:** Return JSON-serializable dictionaries/lists for tools (`List[Dict[str, Any]]`, `Dict[str, Any]`) as used in `src/fde_sql_mcp/server.py` and `src/fde_sql_mcp/tools/databases.py`.

## Module Design

**Exports:** Keep package exports minimal (`__version__` in `src/fde_sql_mcp/__init__.py`); place operational APIs in dedicated modules (`config`, `clients`, `tools`, `server`).

**Barrel Files:** Not used; import concrete modules/functions directly.

---

*Convention analysis: 2026-04-10*
