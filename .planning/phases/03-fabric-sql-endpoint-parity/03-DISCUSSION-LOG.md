# Phase 3: Fabric SQL Endpoint Parity - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves alternatives considered.

**Date:** 2026-04-10
**Phase:** 03-fabric-sql-endpoint-parity
**Mode:** auto (chain)
**Areas discussed:** execution contract, endpoint configuration, metadata parity, safety scope

---

## Execution Contract

| Option | Description | Selected |
|--------|-------------|----------|
| Keep existing SQL/metadata tool signatures and route internally | Preserve prompt compatibility and additive behavior | ✓ |
| Add Fabric-specific query tools | More explicit but breaks shared contract expectation | |

**User's choice:** Auto-selected recommended option: keep shared tool contract.
**Notes:** Aligns with ROADMAP/REQUIREMENTS and phase-2 decisions (`CONF-02`, additive tooling).

---

## Fabric Endpoint Configuration

| Option | Description | Selected |
|--------|-------------|----------|
| Add explicit endpoint mapping config by workspace + endpoint type | Deterministic, governed, no runtime discovery complexity | ✓ |
| Infer endpoints dynamically from workspace names | Implicit and fragile without guaranteed naming conventions | |

**User's choice:** Auto-selected recommended option: explicit mapping config.
**Notes:** Supports allowlist governance and deterministic routing for `core_dw`/`core_lh`.

---

## Metadata Parity

| Option | Description | Selected |
|--------|-------------|----------|
| Route all metadata SQL helpers through shared target-aware execution | Enables parity where Fabric SQL supports metadata views | ✓ |
| Keep metadata on on-prem only and fail on Fabric | Simpler but does not satisfy FAB-05 | |

**User's choice:** Auto-selected recommended option: shared target-aware execution path.
**Notes:** FAB-05 requires continuation across targets where supported.

---

## Safety Scope

| Option | Description | Selected |
|--------|-------------|----------|
| SQL-only Fabric operations through existing ODBC path | Meets SAFE-04 and project scope constraints | ✓ |
| Add Fabric non-SQL operation surface | Out of scope and increases threat surface | |

**User's choice:** Auto-selected recommended option: SQL-only.
**Notes:** No new non-SQL MCP tools are introduced in phase 3.

---

## the agent's Discretion

- Exact internal config schema naming and parser helpers for endpoint mapping.
- Exact helper factoring between `tools/databases.py` and `clients/sql.py`.

## Deferred Ideas

- None beyond previously tracked roadmap deferrals.
