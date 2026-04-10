# Stack Research

**Domain:** Dual-target SQL MCP (on-prem SQL Server + Microsoft Fabric SQL endpoints)
**Researched:** 2026-04-10
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12.x (minimum 3.10) | MCP server runtime | Matches existing codebase, supports current `mcp` releases, and keeps migration risk low. |
| `mcp[cli]` | 1.27.0 | MCP transport/tool runtime | Already used; current stable line and fully sufficient for slim SQL tool surface. |
| `pyodbc` | 5.3.0 | Single DB driver abstraction for both on-prem SQL Server and Fabric SQL endpoints | Keeps one SQL client path for both targets; no ORM overhead; direct control of connection/auth keywords. |
| Microsoft ODBC Driver for SQL Server | 18.6+ (18.x required) | Native SQL connectivity + Entra auth modes | Fabric docs require ODBC 18+ and Entra auth for Warehouse/Lakehouse SQL endpoints. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `azure-identity` | 1.25.3 | Optional token brokerage (`ClientSecretCredential` / `InteractiveBrowserCredential`) | Use if you choose access-token mode (`SQL_COPT_SS_ACCESS_TOKEN`) instead of ODBC `Authentication=` keyword mode. |
| `tenacity` | 9.1.4 | Retry policy for transient SQL/Fabric failures | Use for connection open and query execution retries with small bounded backoff. |
| `pydantic` (or keep stdlib dataclass config) | 2.12.5 | Strict config validation for dual-target settings | Use only if config complexity grows; for current slim scope, stdlib dataclass remains acceptable. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `pytest` | Regression tests for read-only enforcement and target switching | Add matrix tests for `onprem` vs `fabric` targets with same tool behavior. |
| `ruff` | Lint/format gate | Enforce consistency as auth/connection branches are added. |

## Implementation Approach (Recommended 2026)

1. Keep one SQL execution layer (`pyodbc`) and add a target-aware connection factory:
   - `target=onprem`: existing `Trusted_Connection=yes` path.
   - `target=fabric`: ODBC 18 + Entra auth path.
2. Use auth precedence for Fabric exactly as requested:
   - If `FABRIC_TENANT_ID`, `FABRIC_CLIENT_ID`, `FABRIC_CLIENT_SECRET` are all present: use service principal auth.
   - Otherwise: use interactive browser-capable auth.
3. For service principal mode (slimmest path), use ODBC keyword auth:
   - `Authentication=ActiveDirectoryServicePrincipal;UID=<client_id>;PWD=<client_secret>;Encrypt=yes;TrustServerCertificate=no`
4. For interactive fallback:
   - `Authentication=ActiveDirectoryInteractive` (Windows ODBC driver behavior), with explicit `Encrypt=yes`.
5. Enforce Fabric scope in config/code (hard allowlists):
   - Workspaces: `fde_core_data_dev`, `fde_core_data_stg`, `fde_core_data_prod` (and/or known workspace IDs).
   - Databases: `core_dw`, `core_lh`.
6. Keep SQL-only/read-only boundary unchanged:
   - Reuse existing read-only validator for both targets.
   - Continue enforcing max rows/query length.
7. Fabric-specific safety requirements:
   - Always set `Database`/`Initial Catalog` explicitly for Fabric connections.
   - Do not implement SQL authentication for Fabric (unsupported).
   - Document initial SPN Fabric token bootstrap requirement via Fabric REST API for newly created SPNs.

## Installation

```bash
# Core runtime
pip install "mcp[cli]==1.27.0" "pyodbc==5.3.0"

# Optional (token-broker auth path + retries)
pip install "azure-identity==1.25.3" "tenacity==9.1.4"

# Dev
pip install -U pytest ruff
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `pyodbc` direct SQL client | SQLAlchemy + `mssql+pyodbc` | Use only if you need ORM/session features (not needed for MCP read-only query tools). |
| ODBC `Authentication=ActiveDirectoryServicePrincipal/Interactive` | Access-token injection via `SQL_COPT_SS_ACCESS_TOKEN` + `azure-identity` | Use token injection if you need uniform cross-platform interactive behavior or stricter token lifecycle control. |
| Single MCP tool surface with target switch | Separate Fabric MCP server | Use separate server only if governance requires strict process-level isolation. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `ActiveDirectoryPassword` | Deprecated and incompatible with modern MFA/Conditional Access guidance | `ActiveDirectoryInteractive` for user flow, `ActiveDirectoryServicePrincipal` for app flow |
| SQL authentication to Fabric | Fabric Warehouse/Lakehouse SQL endpoints do not support SQL auth | Microsoft Entra auth only |
| Adding Fabric management APIs/notebook/pipeline features in this milestone | Expands scope beyond SQL querying and increases security/maintenance burden | Keep integration limited to SQL endpoint connectivity + existing read-only tools |
| `TrustServerCertificate=yes` for Fabric by default | Weakens TLS trust guarantees for internet-accessed cloud endpoint | `Encrypt=yes;TrustServerCertificate=no` |

## Stack Patterns by Variant

**If running unattended automation (service identity):**
- Use ODBC `ActiveDirectoryServicePrincipal` with env-provided client secret.
- Because it is non-interactive and aligns to requested `FABRIC_*` secret-based auth flow.

**If running local analyst/dev sessions without secrets configured:**
- Use ODBC `ActiveDirectoryInteractive` browser flow.
- Because it supports MFA/Conditional Access and avoids storing user passwords.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `mcp==1.27.0` | Python `>=3.10` | Prefer Python 3.12 for 2026 baseline. |
| `pyodbc==5.3.0` | ODBC Driver 18.x | Fabric docs explicitly require ODBC 18+. |
| ODBC Driver `18.6+` | Fabric SQL endpoints (Warehouse + Lakehouse SQL endpoint) | Use Entra auth; set `Database`/`Initial Catalog`. |
| `azure-identity==1.25.3` | Python `>=3.9` | Optional dependency only if token-attribute auth path is implemented. |

## Sources

- https://learn.microsoft.com/en-us/fabric/data-warehouse/how-to-connect — verified ODBC 18+ requirement, Entra auth requirement, and `Initial Catalog` guidance. (HIGH)
- https://learn.microsoft.com/en-us/fabric/data-warehouse/connectivity — verified SQL auth not supported and connectivity constraints for Fabric SQL endpoints. (HIGH)
- https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-sql-analytics-endpoint — verified Lakehouse SQL endpoint is read-only query surface and shares DW engine/limitations. (HIGH)
- https://learn.microsoft.com/en-us/fabric/data-warehouse/entra-id-authentication — verified Entra auth modes and service principal support for Fabric SQL connection scenarios. (HIGH)
- https://learn.microsoft.com/en-us/fabric/data-warehouse/service-principals — verified SPN prerequisites and token bootstrap/renewal caveats for Fabric control plane. (HIGH)
- https://learn.microsoft.com/en-us/sql/connect/odbc/using-azure-active-directory?view=sql-server-ver15 — verified ODBC auth keyword modes, `ActiveDirectoryServicePrincipal` availability (17.7+), and deprecation of `ActiveDirectoryPassword`. (HIGH)
- https://pypi.org/pypi/mcp/json — verified current package version metadata (`1.27.0`). (MEDIUM)
- https://pypi.org/pypi/pyodbc/json — verified current package version metadata (`5.3.0`). (MEDIUM)
- https://pypi.org/pypi/azure-identity/json — verified current package version metadata (`1.25.3`). (MEDIUM)

---
*Stack research for: dual-target SQL MCP (on-prem + Fabric SQL endpoints)*
*Researched: 2026-04-10*
