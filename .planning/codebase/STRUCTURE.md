# Codebase Structure

**Analysis Date:** 2026-04-10

## Directory Layout

```text
fde_sql_mcp/
├── .planning/                  # Planning artifacts and generated codebase maps
│   └── codebase/               # Mapper output documents (including this file)
├── src/                        # Python package source root
│   └── fde_sql_mcp/            # Main application package
│       ├── clients/            # SQL connectivity layer (pyodbc wrapper)
│       ├── tools/              # SQL metadata/query implementations
│       ├── config.py           # Runtime settings loader/normalizer
│       └── server.py           # MCP transport and tool registration
├── tmp/                        # Local scratch/output directory (ignored)
├── pyproject.toml              # Package metadata and MCP entrypoint
├── requirements.txt            # Runtime dependency list
├── README.md                   # Usage and operation documentation
└── fde_sql_mcp.config.template.json  # Non-secret config template
```

## Directory Purposes

**`src/fde_sql_mcp/`:**
- Purpose: Place all importable production Python code.
- Contains: server, config, SQL client, and tool implementation modules.
- Key files: `src/fde_sql_mcp/server.py`, `src/fde_sql_mcp/config.py`, `src/fde_sql_mcp/clients/sql.py`, `src/fde_sql_mcp/tools/databases.py`.

**`src/fde_sql_mcp/clients/`:**
- Purpose: Keep external system access primitives and connection helpers.
- Contains: SQL Server connection abstraction (`sql.py`).
- Key files: `src/fde_sql_mcp/clients/sql.py`.

**`src/fde_sql_mcp/tools/`:**
- Purpose: Keep MCP-facing domain operations separate from transport.
- Contains: read-only query and metadata listing implementations.
- Key files: `src/fde_sql_mcp/tools/databases.py`.

**`.planning/codebase/`:**
- Purpose: Store generated architecture/convention intelligence for downstream GSD commands.
- Contains: mapper output markdown docs.
- Key files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`.

## Key File Locations

**Entry Points:**
- `src/fde_sql_mcp/server.py`: MCP server bootstrap, tool decorators, and `run()` lifecycle.
- `pyproject.toml`: default MCP entrypoint `fde_sql_mcp.server:run`.

**Configuration:**
- `src/fde_sql_mcp/config.py`: settings resolution from local JSON + environment.
- `fde_sql_mcp.config.template.json`: template for required local config fields.
- `.gitignore`: excludes `fde_sql_mcp.config.json` and runtime artifacts.

**Core Logic:**
- `src/fde_sql_mcp/tools/databases.py`: read-only validator and SQL metadata queries.
- `src/fde_sql_mcp/clients/sql.py`: connection-string assembly and pyodbc context manager.

**Testing:**
- Not detected in repository (`tests/`, `*.test.py`, and `*.spec.py` are not present).

## Naming Conventions

**Files:**
- Use lowercase snake_case module names for Python files (example: `src/fde_sql_mcp/tools/databases.py`).
- Keep package path aligned to project name (example: `src/fde_sql_mcp/`).

**Directories:**
- Use lowercase names for package directories (example: `src/fde_sql_mcp/clients/`, `src/fde_sql_mcp/tools/`).
- Separate directories by responsibility: `clients` for connectivity, `tools` for operations.

## Where to Add New Code

**New Feature:**
- Primary code: add new implementation functions in `src/fde_sql_mcp/tools/` (new module or extend `src/fde_sql_mcp/tools/databases.py`).
- MCP exposure: register new `@mcp.tool` wrapper in `src/fde_sql_mcp/server.py` delegating via `asyncio.to_thread(...)`.
- Tests: create a new `tests/` directory at repo root and mirror package layout (`tests/tools/`, `tests/clients/`) since no test tree exists yet.

**New Component/Module:**
- SQL or external system connectors: place in `src/fde_sql_mcp/clients/`.
- Config parsing/normalization: extend `src/fde_sql_mcp/config.py` only; keep consumers reading `settings`.

**Utilities:**
- Shared helpers tied to SQL querying should remain in `src/fde_sql_mcp/tools/databases.py` until a distinct utility module is justified.
- Shared cross-module helpers can be added as new modules under `src/fde_sql_mcp/` with snake_case naming.

## Special Directories

**`.planning/`:**
- Purpose: planning intelligence and workflow artifacts.
- Generated: Yes.
- Committed: Yes.

**`tmp/`:**
- Purpose: local temporary files.
- Generated: Yes.
- Committed: No (ignored via `.gitignore`).

**`.venv/`:**
- Purpose: local Python virtual environment.
- Generated: Yes.
- Committed: No (ignored via `.gitignore`).

---

*Structure analysis: 2026-04-10*
