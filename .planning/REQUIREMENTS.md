# Requirements: FDE SQL MCP

**Defined:** 2026-04-10
**Core Value:** Users can query approved SQL data targets with one consistent, read-only MCP interface regardless of whether the data lives on-prem or in Fabric.

## v1 Requirements

### Routing and Target Selection

- [x] **ROUTE-01**: User can run the existing read-only SQL tools against on-prem SQL Server without changing current prompt patterns.
- [x] **ROUTE-02**: User can explicitly switch active query environment between `onprem` and `fabric`.
- [x] **ROUTE-03**: User can target Fabric environment through natural language (for example, "query fabric prod lakehouse for y") and the server resolves a deterministic target.
- [x] **ROUTE-04**: Query responses include resolved target context (environment, workspace, endpoint type, database) so users can verify where queries ran.

### Fabric SQL Endpoint Support

- [x] **FAB-01**: User can list/select Fabric workspaces only from an allowlisted set (`fde_core_data_dev`, `fde_core_data_stg`, `fde_core_data_prod`) or mapped workspace IDs.
- [ ] **FAB-02**: User can set/query Fabric Warehouse SQL endpoint targets for allowed `core_dw` database contexts.
- [ ] **FAB-03**: User can set/query Fabric Lakehouse SQL endpoint targets for allowed `core_lh` database contexts.
- [ ] **FAB-04**: User can execute read-only SQL queries against the selected Fabric endpoint using the same MCP SQL tool contract.
- [ ] **FAB-05**: Existing metadata discovery tools continue to function with target-aware behavior (on-prem and Fabric where supported).

### Authentication

- [x] **AUTH-01**: If `FABRIC_TENANT_ID`, `FABRIC_CLIENT_ID`, and `FABRIC_CLIENT_SECRET` are all set, Fabric auth uses client-secret flow.
- [x] **AUTH-02**: If any client-secret variables are missing, Fabric auth falls back to browser-capable default auth without blocking startup.
- [x] **AUTH-03**: Fabric auth behavior is single-tenant and uses one tenant context for all allowlisted Fabric workspaces.

### Safety and Governance

- [ ] **SAFE-01**: Read-only SQL validation is enforced for both on-prem and Fabric execution paths.
- [ ] **SAFE-02**: Query guardrails (max rows, max query characters, timeout) apply consistently across on-prem and Fabric targets.
- [x] **SAFE-03**: Queries are rejected when resolved Fabric workspace/database targets are outside the allowlist.
- [ ] **SAFE-04**: Scope remains SQL-only; no write operations or non-SQL Fabric operations are exposed by this MCP.

### Configuration and Developer UX

- [x] **CONF-01**: Configuration supports both on-prem SQL settings and Fabric settings in one project config model.
- [x] **CONF-02**: Tool descriptions remain mostly unchanged while implementation becomes environment-aware to minimize prompt/token overhead.
- [ ] **CONF-03**: Documentation explains dual-environment setup, auth precedence, and examples for both explicit and natural-language targeting.

## v2 Requirements

### Diagnostics and Operations

- **OPS-01**: User can run a dedicated diagnostics tool to confirm active auth mode, principal identity, and target allowlist evaluations.
- **OPS-02**: Query execution emits structured audit logs and metrics (duration, row count, target context, error class) with sensitive-value-safe formatting.

### Performance

- **PERF-01**: Metadata-heavy operations use short-lived caching with safe invalidation on target/auth changes.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fabric pipelines/notebooks/project orchestration support | This milestone is intentionally slim and SQL-query only |
| Non-SQL Fabric workloads (Spark, OneLake file APIs) | Not required for SQL endpoint querying objective |
| Write/DDL/DML query capability | Violates read-only safety boundary |
| Multi-tenant Fabric auth and tenant routing | Single-tenant is sufficient and explicitly requested |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ROUTE-01 | Phase 1 | Complete |
| ROUTE-02 | Phase 2 | Complete |
| ROUTE-03 | Phase 2 | Complete |
| ROUTE-04 | Phase 2 | Complete |
| FAB-01 | Phase 2 | Complete |
| FAB-02 | Phase 3 | Pending |
| FAB-03 | Phase 3 | Pending |
| FAB-04 | Phase 3 | Pending |
| FAB-05 | Phase 3 | Pending |
| AUTH-01 | Phase 1 | Complete |
| AUTH-02 | Phase 1 | Complete |
| AUTH-03 | Phase 1 | Complete |
| SAFE-01 | Phase 4 | Pending |
| SAFE-02 | Phase 4 | Pending |
| SAFE-03 | Phase 2 | Complete |
| SAFE-04 | Phase 3 | Pending |
| CONF-01 | Phase 1 | Complete |
| CONF-02 | Phase 2 | Complete |
| CONF-03 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 19 total
- Mapped to phases: 19
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-10*
*Last updated: 2026-04-10 after roadmap mapping*
