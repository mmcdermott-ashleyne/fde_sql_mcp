# Roadmap: FDE SQL MCP

## Overview

This roadmap delivers a slim, SQL-only dual-target MCP server where users keep one shared read-only tool surface while safely switching between on-prem SQL Server and allowlisted Fabric SQL endpoints.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Dual-Target Foundation and Auth** - Establish dual config and deterministic Fabric auth while preserving current on-prem behavior. (completed 2026-04-10)
- [x] **Phase 2: Target Routing and Governance** - Add explicit and natural-language routing with strict allowlisted target resolution. (completed 2026-04-10)
- [x] **Phase 3: Fabric SQL Endpoint Parity** - Enable allowed Warehouse and Lakehouse querying with the shared read-only MCP tool contract. (completed 2026-04-10)
- [x] **Phase 4: Safety Guardrails and Operator Docs** - Enforce cross-target read-only guardrails and document dual-environment usage. (completed 2026-04-14)

## Phase Details

### Phase 1: Dual-Target Foundation and Auth
**Goal**: Users can run the server with both on-prem and Fabric settings and get deterministic single-tenant Fabric authentication without breaking existing on-prem flows.
**Depends on**: Nothing (first phase)
**Requirements**: ROUTE-01, AUTH-01, AUTH-02, AUTH-03, CONF-01
**Success Criteria** (what must be TRUE):
  1. User can run existing read-only SQL tools against on-prem SQL Server without changing current prompt patterns.
  2. User can start the server with one configuration model that includes both on-prem and Fabric settings.
  3. User can authenticate to Fabric with client-secret flow when `FABRIC_TENANT_ID`, `FABRIC_CLIENT_ID`, and `FABRIC_CLIENT_SECRET` are all set.
  4. User can still use Fabric through browser-capable fallback auth when any client-secret variable is missing, without startup failure.
  5. User can run Fabric operations under one tenant context across the allowlisted environments.
**Plans**: TBD

### Phase 2: Target Routing and Governance
**Goal**: Users can deterministically select/query target environments with clear execution context and hard allowlist enforcement.
**Depends on**: Phase 1
**Requirements**: ROUTE-02, ROUTE-03, ROUTE-04, FAB-01, SAFE-03, CONF-02
**Success Criteria** (what must be TRUE):
  1. User can explicitly switch active query environment between `onprem` and `fabric`.
  2. User can target Fabric via natural language and get deterministic target resolution.
  3. User sees resolved target context in responses (environment, workspace, endpoint type, database).
  4. User can list/select Fabric workspaces only from `fde_core_data_dev`, `fde_core_data_stg`, and `fde_core_data_prod` (or mapped IDs).
  5. User keeps the same read-only MCP tool surface while target-aware routing happens behind the scenes, and out-of-allowlist targets are rejected.
**Plans**: TBD

### Phase 3: Fabric SQL Endpoint Parity
**Goal**: Users can query approved Fabric Warehouse and Lakehouse SQL endpoints using the same read-only MCP SQL contract used for on-prem.
**Depends on**: Phase 2
**Requirements**: FAB-02, FAB-03, FAB-04, FAB-05, SAFE-04
**Success Criteria** (what must be TRUE):
  1. User can set and query Fabric Warehouse targets only for allowed `core_dw` database contexts.
  2. User can set and query Fabric Lakehouse targets only for allowed `core_lh` database contexts.
  3. User can execute read-only SQL queries against selected Fabric endpoints through the existing MCP SQL tool contract.
  4. User can run metadata discovery tools with target-aware behavior across on-prem and Fabric where supported.
  5. User cannot access non-SQL Fabric operations from this MCP server.
**Plans**: TBD

### Phase 4: Safety Guardrails and Operator Docs
**Goal**: Users get consistent read-only safety enforcement across both targets and clear documentation for dual-environment setup and usage.
**Depends on**: Phase 3
**Requirements**: SAFE-01, SAFE-02, CONF-03
**Success Criteria** (what must be TRUE):
  1. User sees read-only SQL validation enforced for both on-prem and Fabric execution paths.
  2. User sees max rows, max query length, and timeout guardrails enforced consistently across on-prem and Fabric.
  3. User can follow documentation to configure dual-environment setup and auth precedence correctly.
  4. User can follow documentation examples for explicit environment switching and natural-language target selection.
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Dual-Target Foundation and Auth | 1/1 | Complete    | 2026-04-10 |
| 2. Target Routing and Governance | 1/1 | Complete   | 2026-04-10 |
| 3. Fabric SQL Endpoint Parity | 1/1 | Complete   | 2026-04-10 |
| 4. Safety Guardrails and Operator Docs | 1/1 | Complete   | 2026-04-14 |
