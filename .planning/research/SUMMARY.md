# Project Research Summary

**Project:** FDE SQL MCP
**Domain:** Dual-target read-only SQL MCP connector (on-prem SQL Server + Microsoft Fabric SQL endpoints)
**Researched:** 2026-04-10
**Confidence:** MEDIUM

## Executive Summary

This project is a production-focused, read-only MCP SQL connector that must keep one stable tool surface while supporting two backends: on-prem SQL Server and Fabric Warehouse/Lakehouse SQL endpoints. The research converges on a thin-wrapper architecture: keep `server.py` contracts stable, centralize routing/policy decisions, and run all execution through a shared guardrailed SQL service with target-specific connectors.

The recommended implementation path is to preserve current on-prem behavior first, then layer deterministic routing and per-client context, then plug in Fabric connectivity with strict auth precedence and allowlists. Use Python 3.12 + `mcp[cli]` + `pyodbc` with ODBC Driver 18.x, keep read-only guardrails immutable, and enforce canonical target governance (workspace IDs, allowed catalogs, explicit environment mapping).

The highest risks are identity drift from ambiguous auth fallback, Fabric permission/prerequisite misconfiguration, and SQL Server assumptions leaking into Fabric execution (`SET ROWCOUNT`). Mitigation is explicit credential-mode selection, tenant/workspace preflight checks, target capability profiles, and phase-gated validation suites that prove parity and least privilege before rollout.

## Key Findings

### Recommended Stack

Use a conservative stack aligned with current code to minimize migration risk: Python 3.12.x, `mcp[cli]==1.27.0`, `pyodbc==5.3.0`, and Microsoft ODBC Driver 18.6+ for Fabric compatibility. Keep one SQL execution path and introduce a target-aware connector factory rather than adding a second tool family.

**Core technologies:**
- `Python 3.12.x`: MCP runtime baseline and compatibility with current library ecosystem.
- `mcp[cli] 1.27.0`: Stable MCP transport/tool runtime already aligned with repo patterns.
- `pyodbc 5.3.0`: Single driver abstraction for both SQL Server and Fabric SQL endpoints.
- `ODBC Driver 18.6+`: Required for modern Entra auth and Fabric SQL endpoint support.
- `azure-identity 1.25.3` (optional): Token brokerage path if access-token mode is chosen.
- `tenacity 9.1.4` (optional): Bounded retries for transient Fabric/ODBC failures.

### Expected Features

The MVP should prioritize a unified read-only experience, deterministic routing/governance, and strong operational safety. Differentiators should improve UX and diagnostics without widening scope into write/admin surfaces.

**Must have (table stakes):**
- Unified read-only query and metadata tooling across on-prem and Fabric targets.
- Deterministic auth model: on-prem Windows auth, Fabric SPN-first with controlled interactive fallback.
- Hard allowlists for approved Fabric workspaces/databases and explicit resolved-target behavior.
- Shared read-only validator with enforced row/time/query limits and normalized errors.
- Production observability for query/audit metrics and failure taxonomy.

**Should have (competitive):**
- Natural-language environment selection that resolves to canonical allowlisted targets and echoes resolution.
- Permission diagnostics helper for common auth/authorization failures.
- Short-TTL metadata caching with invalidation on target/auth changes.

**Defer (v2+):**
- Capability negotiation endpoint for clients (feature flags by target).
- Policy engine for team/tool-specific restriction rules.
- Any write/DDL/DML or broad Fabric management/orchestration features.

### Architecture Approach

Adopt a layered architecture that isolates routing, policy, and connector concerns from MCP tools. Keep wrappers thin, route once, apply shared guardrails once, then execute through target-specific adapters. This keeps behavior consistent while preventing code duplication and target drift.

**Major components:**
1. MCP tool wrappers (`server.py`) — stable public contract, minimal logic.
2. Routing/context/policy core — resolve target, persist client context, enforce allowlists.
3. Shared read-only SQL service — unified validation, limits, and execution semantics.
4. Connector factory/adapters — on-prem Trusted Connection path and Fabric Entra path.
5. Fabric endpoint resolver — workspace/item resolution to SQL server/database with optional cache.

### Critical Pitfalls

1. **Non-deterministic auth fallback** — enforce explicit credential-mode routing and fail closed on ambiguous env state.
2. **Fabric SPN prerequisites not enabled** — add startup/preflight checks for tenant settings, group allowlists, and workspace/item access.
3. **ODBC auth mode mixing** — keep auth modes mutually exclusive and always set cloud TLS explicitly (`Encrypt=yes`, `TrustServerCertificate=no`).
4. **Name-based allowlisting drift** — validate against canonical IDs/hosts/catalogs and reject ambiguity.
5. **SQL Server-only query wrapper leaks into Fabric** — implement target capability profiles and remove unsupported statements (notably `SET ROWCOUNT`) for Fabric.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Auth and Connectivity Foundation
**Rationale:** All other work depends on deterministic identity and successful dual-target connection semantics.
**Delivers:** Explicit auth precedence, Fabric SPN + controlled interactive fallback, ODBC mode matrix, tenant/workspace preflight checks.
**Addresses:** Dual auth model, deterministic errors, secure baseline connectivity.
**Avoids:** Non-deterministic fallback, SPN prerequisite failures, ODBC mode-mixing regressions.

### Phase 2: Routing and Governance Controls
**Rationale:** Target safety boundaries must be enforced before broad execution enablement.
**Delivers:** Route resolver, per-client target context store, canonical allowlists (workspace IDs/hosts/catalogs), explicit target resolution echo.
**Uses:** `core/routing.py`, `core/context_store.py`, `core/policies.py` style split.
**Implements:** Target policy enforcement and deterministic environment switching.

### Phase 3: Dual-Target Query Engine Abstraction
**Rationale:** Shared behavior parity is the core product value and must be proven after routing/auth are stable.
**Delivers:** Target-agnostic read-only service, connector factory, Fabric execution adapter, capability-aware row limiting and metadata behavior.
**Addresses:** Unified query contract, schema introspection parity, read-only guardrails across both targets.
**Avoids:** SQL Server-specific execution assumptions breaking Fabric.

### Phase 4: UX and Diagnostics Enhancements
**Rationale:** After correctness and safety, improve operator/user effectiveness without scope expansion.
**Delivers:** Natural-language target resolver (canonicalized), permission diagnostics helper, richer actionable error mapping.
**Addresses:** Environment switching usability, supportability, access troubleshooting.
**Avoids:** Ambiguous target selection and opaque auth/permission failures.

### Phase 5: Reliability and Observability Hardening
**Rationale:** Productionization should follow functional parity to reduce operational risk at scale.
**Delivers:** Structured audit logs, retry policy for transient failures, metadata cache with TTL/invalidation, reliability SLO checks.
**Addresses:** Production observability and resilience table stakes.
**Avoids:** Silent transient failure churn, schema-call latency bottlenecks, poor incident triage.

### Phase Ordering Rationale

- Auth/connectivity precedes routing and query work because route correctness is meaningless without deterministic principal identity.
- Governance is sequenced before Fabric execution parity to prevent accidental cross-environment access during rollout.
- Query abstraction is isolated before UX work so user-facing improvements do not mask correctness/safety gaps.
- Reliability/observability is last because baseline behavior must be stable before tuning retries/caching and setting operator metrics.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** Fabric tenant/SPN enablement and ODBC auth-mode behavior can vary by environment and policy posture.
- **Phase 3:** Fabric SQL surface compatibility details (metadata/query dialect parity) need targeted validation cases.
- **Phase 4:** Natural-language resolver needs clear ambiguity policy and user confirmation semantics.

Phases with standard patterns (skip research-phase):
- **Phase 2:** Routing/context/allowlist enforcement follows established internal patterns from existing MCP servers.
- **Phase 5:** Logging, bounded retry, and short-TTL cache patterns are well-established and low-ambiguity.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Versions and constraints are backed by official Microsoft/PyPI docs and align with existing repo runtime. |
| Features | MEDIUM | Prioritization is strong, but some differentiators (NL routing/capability exposure) remain product-policy choices. |
| Architecture | HIGH | Matches current code shape and proven patterns from sibling Fabric MCP implementation. |
| Pitfalls | HIGH | Risks are concrete, source-backed, and mapped to prevention/verification phases. |

**Overall confidence:** MEDIUM

### Gaps to Address

- Fabric endpoint metadata parity: confirm exact unsupported/variant operations and lock a target capability matrix during Phase 3 planning.
- Tenant/network prerequisites: validate environment-specific SPN, firewall, and role setups in dev/stg/prod before enabling by default.
- Security-mode behavior in SQL analytics endpoints: verify least-privilege role outcomes (Viewer vs elevated roles) with explicit test cases.
- Observability privacy policy: define what SQL text/parameters can be logged to balance auditability with data sensitivity.

## Sources

### Primary (HIGH confidence)
- `.planning/research/STACK.md` — runtime, driver, auth, and version recommendations.
- `.planning/research/ARCHITECTURE.md` — target layering, component boundaries, and sequencing.
- `.planning/research/PITFALLS.md` — phase-mapped risk register and mitigations.
- https://learn.microsoft.com/en-us/fabric/data-warehouse/connectivity — Fabric connectivity/auth constraints.
- https://learn.microsoft.com/en-us/fabric/data-warehouse/entra-id-authentication — Entra auth and service principal model.
- https://learn.microsoft.com/en-us/fabric/data-warehouse/tsql-surface-area — unsupported/limited T-SQL surface for Fabric Warehouse.
- https://learn.microsoft.com/en-us/sql/connect/odbc/using-azure-active-directory?view=sql-server-ver17 — ODBC Entra auth modes and constraints.

### Secondary (MEDIUM confidence)
- `.planning/research/FEATURES.md` — prioritization, differentiators, and anti-features.
- `.planning/PROJECT.md` — scope boundaries and active requirements.
- https://pypi.org/pypi/mcp/json — package version metadata.
- https://pypi.org/pypi/pyodbc/json — package version metadata.

### Tertiary (LOW confidence)
- N/A (no single-source critical recommendation retained without corroboration).

---
*Research completed: 2026-04-10*
*Ready for roadmap: yes*
