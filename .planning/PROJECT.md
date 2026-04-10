# FDE SQL MCP

## What This Is

FDE SQL MCP is a read-only MCP server for SQL querying and schema discovery. It currently supports on-prem SQL Server through Windows authentication and is being expanded to also support Microsoft Fabric SQL endpoints (Lakehouse/Warehouse) using the same tool experience. The primary users are internal analysts and engineers who need consistent, safe SQL access across environments.

## Core Value

Users can query approved SQL data targets with one consistent, read-only MCP interface regardless of whether the data lives on-prem or in Fabric.

## Requirements

### Validated

- ✓ Read-only MCP SQL tools for on-prem SQL Server metadata and querying — existing
- ✓ Windows-authenticated SQL Server connectivity via ODBC in the MCP runtime — existing
- ✓ Config-driven SQL guardrails (row/query limits and read-only enforcement) — existing
- ✓ Thin MCP tool wrappers delegating to implementation modules — existing

### Active

- [ ] Add Fabric SQL endpoint support for Lakehouse and Warehouse querying only
- [ ] Support Fabric authentication via client secret (`FABRIC_TENANT_ID`, `FABRIC_CLIENT_ID`, `FABRIC_CLIENT_SECRET`)
- [ ] Default to browser-capable auth only when client-secret variables are not fully set
- [ ] Add dual configuration support so on-prem and Fabric settings coexist and can be switched easily
- [ ] Restrict Fabric access to hardcoded workspaces: `fde_core_data_dev`, `fde_core_data_stg`, `fde_core_data_prod`
- [ ] Restrict Fabric target databases to `core_dw` and `core_lh`
- [ ] Reuse the existing read-only tool surface for both target environments to minimize token/context overhead
- [ ] Support both explicit environment switching and natural-language environment selection

### Out of Scope

- Full Fabric management/orchestration features (pipelines, notebooks, project orchestration) — this effort is SQL endpoint querying only
- Fabric non-SQL compute flows (Spark notebooks, OneLake file operations) — not needed for this MCP scope
- Write/DDL/DML operations against Fabric or on-prem SQL — read-only usage is a hard safety boundary
- Multi-tenant Fabric auth strategy — single-tenant is sufficient for current needs

## Context

This repository currently implements on-prem SQL Server MCP tooling with Windows auth and strong read-only query validation. The new direction is to keep the server lean while adding Fabric SQL endpoint access, explicitly using patterns from `C:\Users\mmcdermott\OneDrive - Factory Direct of Edison\dev\repositories\fde_fabric_mcp` for Azure auth and SQL token handling. The user wants one MCP server that can bounce between on-prem and Fabric contexts with minimal extra tool surface and minimal prompt-token overhead.

## Constraints

- **Security**: Read-only SQL behavior must remain enforced across on-prem and Fabric targets — prevents accidental writes
- **Platform**: Fabric auth is single-tenant and should prefer client-secret when configured — aligns with service principal operations
- **Scope**: Fabric support is limited to Warehouse/Lakehouse SQL endpoint querying — keeps implementation slim
- **Governance**: Fabric workspaces and databases must be allowlisted in code/config — limits accidental access drift
- **UX**: Existing tool semantics should be retained while adding target awareness — avoids prompt/tool churn

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Reuse the same read-only SQL tools across environments | Reduces cognitive load and token usage while preserving current workflows | — Pending |
| Fabric auth precedence is client-secret first, browser fallback otherwise | Supports unattended secure auth when configured, with local fallback for dev use | — Pending |
| Restrict Fabric to three named workspaces plus allowlisted workspace IDs | Enforces environment boundaries (`dev/stg/prod`) while allowing deterministic ID matching | — Pending |
| Keep this effort SQL-only and exclude broader Fabric feature parity | Delivers high-value integration quickly with low implementation risk | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-10 after initialization*
