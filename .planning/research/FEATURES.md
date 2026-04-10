# Feature Research

**Domain:** Production-grade MCP SQL connector (on-prem SQL Server + Fabric SQL endpoints)
**Researched:** 2026-04-10
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Unified read-only query tooling across both targets | Analysts expect one MCP interface, not separate tool families per backend | MEDIUM | Keep one `run_readonly_query` contract and target-routing behind the scenes; aligns with PROJECT core value |
| Strict read-only enforcement + query/row/time limits | Production SQL connectors are expected to prevent accidental writes and runaway queries | MEDIUM | Enforce SELECT/CTE-only validation, row caps, and timeouts for SQL Server and Fabric |
| Dual auth model (Windows auth for on-prem, Entra for Fabric SPN-first with interactive fallback) | Enterprise environments require non-interactive service auth plus local developer fallback | HIGH | Fabric supports Entra user/SPN auth and ODBC `ActiveDirectoryServicePrincipal`/interactive modes |
| Target governance controls (workspace/database allowlists) | Enterprises require explicit boundary controls between dev/stg/prod and approved datasets | LOW | Hardcode/validate Fabric workspace + database allowlists before query execution |
| Core schema introspection (databases/tables/views/procs/indexes/columns) | Query users expect discovery before writing SQL | MEDIUM | Existing SQL Server metadata tools should stay symmetric where Fabric supports equivalent metadata |
| Deterministic error handling and safe parameter validation | MCP clients expect structured, actionable failures instead of opaque DB driver errors | MEDIUM | Normalize auth/permission/timeout/not-found errors; validate database identifiers before connection-string construction |
| Production observability (query audit logs + metrics) | Operators need traceability for security/compliance and incident triage | MEDIUM | Log tool, target, principal, duration, row_count, truncation, and failure class (without sensitive SQL literals where possible) |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Natural-language environment selection with deterministic resolver | Faster analyst workflow while still preserving strict target control | MEDIUM | Parse phrases like "run in prod warehouse" to allowlisted target IDs; always echo resolved target before execution |
| Capability-aware metadata/query behavior per target | Avoids broken UX when Fabric and SQL Server differ in feature surface | HIGH | Expose capability map and degrade gracefully (for example, unsupported object types/DDL behavior in Fabric endpoints) |
| Cross-target safety profile presets (`dev`, `stg`, `prod`) | Operational consistency and lower misconfiguration risk | LOW | Bundle per-environment defaults for max rows, timeout, and stricter production policies |
| Permission diagnostics helper | Reduces support cycles when users cannot see expected objects/data | MEDIUM | Add tool output hints for role/permission issues (workspace/item/read permissions, SQL grants) |
| Metadata caching with short TTL + invalidation hooks | Better latency on large schemas without stale behavior surprises | MEDIUM | Cache list endpoints by target+principal, invalidate on auth/target switch or TTL expiry |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Write/DDL/DML support in same MCP server | "One connector should do everything" | Violates safety boundary, increases blast radius, and complicates policy controls | Keep read-only connector; create separate privileged write path/server if ever needed |
| Auto-discover and query any Fabric workspace/database in tenant | Convenience during exploration | Breaks governance and environment isolation expectations | Enforce explicit allowlists and deny-by-default routing |
| Query rewriting/auto-fixing SQL inside connector | Convenience when SQL fails | Hides behavior, increases correctness risk, and complicates auditing | Return deterministic errors with optional guidance; keep execution engine non-mutating |
| Broad admin-role reliance for access issues | "It just works" onboarding shortcut | Admin/Contributor roles can bypass fine-grained data controls, creating security drift | Require least-privilege roles and explicit item/share permissions per target |

## Feature Dependencies

```text
[Dual target routing model]
    └──requires──> [Authentication abstraction (Windows + Entra)]
                       └──requires──> [Target governance allowlists]

[Unified read-only query contract]
    └──requires──> [Read-only validator + limits]
                       └──requires──> [Driver-level timeout enforcement]

[Schema introspection parity]
    └──requires──> [Capability map per target]

[Natural-language environment selection] ──enhances──> [Dual target routing model]

[Write/DDL support] ──conflicts──> [Production read-only safety boundary]
```

### Dependency Notes

- **Dual target routing model requires auth abstraction:** routing is meaningless unless each target can be authenticated reliably with predictable precedence rules.
- **Auth abstraction requires governance allowlists:** without allowlists, successful auth can still lead to accidental cross-environment data access.
- **Unified query contract requires validator + limits:** same tool name across targets only works if safety behavior is equally strict.
- **Schema parity requires capability mapping:** SQL Server and Fabric endpoint surfaces differ; capability awareness prevents false promises.
- **Natural-language targeting enhances routing:** it is UX acceleration, not a base dependency.
- **Write support conflicts with read-only boundary:** mixing read/write paths in one connector weakens auditability and least-privilege posture.

## MVP Definition

### Launch With (v1)

Minimum viable product for this milestone.

- [ ] Unified read-only tool contract across on-prem SQL Server and Fabric SQL endpoints
- [ ] Auth precedence + fallback model (Windows auth on-prem; Fabric SPN first, interactive fallback)
- [ ] Hard allowlists for Fabric workspaces/databases and explicit target resolution
- [ ] Read-only validator, row/time limits, and deterministic error normalization
- [ ] Core schema discovery tools with parity notes where Fabric differs

### Add After Validation (v1.x)

- [ ] Natural-language environment selection with explicit resolved-target echo
- [ ] Permission diagnostics helper for common access failures
- [ ] Metadata caching for large-schema performance

### Future Consideration (v2+)

- [ ] Rich capability negotiation endpoint for clients (feature flags by target)
- [ ] Optional policy engine for per-team/per-tool query restrictions

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Unified read-only dual-target querying | HIGH | MEDIUM | P1 |
| Auth abstraction with SPN-first Fabric flow | HIGH | HIGH | P1 |
| Governance allowlists and deterministic routing | HIGH | LOW | P1 |
| Observability and audit logging | HIGH | MEDIUM | P1 |
| Natural-language environment selection | MEDIUM | MEDIUM | P2 |
| Permission diagnostics helper | MEDIUM | MEDIUM | P2 |
| Metadata caching | MEDIUM | MEDIUM | P2 |
| Capability negotiation endpoint | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Single-target SQL MCP connectors | Fabric-management MCP servers | Our Approach |
|---------|----------------------------------|-------------------------------|--------------|
| Query scope | Usually one engine only | Broad Fabric admin/orchestration scope | Keep SQL query scope only, but support both SQL Server and Fabric SQL endpoints |
| Safety model | Often basic read-only checks | Mixed read/write tooling for admin tasks | Strong read-only boundary, deny-by-default target policy |
| Operator visibility | Often minimal logs | Better operational detail for admin workflows | Add production query audit + error taxonomy without bloating tool surface |
| UX for environment switching | Usually manual config changes | Workspace-centric but Fabric-only | Single tool surface with explicit target routing and optional NL targeting |

## Sources

- Local project scope and requirements: `.planning/PROJECT.md`, `README.md`, `src/fde_sql_mcp/server.py`, `.planning/codebase/CONCERNS.md`
- Microsoft Fabric Entra auth for Warehouse/SQL endpoint (auth modes, SPN support, TDS/ODBC guidance): https://learn.microsoft.com/en-us/fabric/data-warehouse/entra-id-authentication
- Microsoft Fabric connectivity/permissions and SQL endpoint access model: https://learn.microsoft.com/en-us/fabric/data-warehouse/share-warehouse-manage-permissions
- OneLake security behavior for SQL analytics endpoints (read-path enforcement and role behavior): https://learn.microsoft.com/en-us/fabric/onelake/security/sql-analytics-endpoint-onelake-security
- Fabric warehouse/SQL endpoint limitations (region, endpoint constraints): https://learn.microsoft.com/en-us/fabric/data-warehouse/limitations
- SQL Server database role reference (`db_datareader`/`db_datawriter` semantics): https://learn.microsoft.com/en-us/sql/relational-databases/security/authentication-access/database-level-roles?view=sql-server-ver16
- MCP transport/session/security-relevant protocol requirements: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports

---
*Feature research for: dual-target MCP SQL connector (SQL Server + Fabric SQL endpoints)*
*Researched: 2026-04-10*
