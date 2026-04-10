---
phase: 03-fabric-sql-endpoint-parity
plan: 01
subsystem: api
tags: [python, mcp, sql-server, fabric, routing, governance]
requires:
  - phase: 02-target-routing-and-governance
    provides: Active target routing with workspace/database allowlist enforcement
provides:
  - Fabric Warehouse/Lakehouse SQL endpoint execution via shared MCP SQL tools
  - Target-aware metadata/query execution across onprem and fabric paths
  - Fail-closed endpoint mapping validation for Fabric workspace/endpoint/database tuples
affects: [phase-4-safety-guardrails-and-operator-docs]
tech-stack:
  added: []
  patterns: [target-aware-connection-resolution, shared-readonly-contract, fail-closed-endpoint-mapping]
key-files:
  created: []
  modified:
    - src/fde_sql_mcp/config.py
    - src/fde_sql_mcp/clients/sql.py
    - src/fde_sql_mcp/tools/databases.py
    - tests/test_settings_fabric.py
    - tests/test_target_routing.py
    - fde_sql_mcp.config.template.json
    - README.md
key-decisions:
  - "Fabric SQL endpoints are configured explicitly via `fabric_sql_endpoint_map` and never inferred implicitly."
  - "Execution routing remains behind the existing MCP SQL tool contract; no Fabric-specific query tool fork."
  - "Fabric execution fails closed on mapping gaps or database/endpoint mismatches."
patterns-established:
  - "One resolver (`_resolve_execution_target`) drives both read-only query and metadata paths."
  - "Connection auth mode is target-derived: SQL auth only when endpoint credentials exist; otherwise trusted connection."
requirements-completed: [FAB-02, FAB-03, FAB-04, FAB-05, SAFE-04]
duration: 15m
completed: 2026-04-10
---

# Phase 3 Plan 01: Fabric SQL Endpoint Parity Summary

**Target-aware Fabric Warehouse/Lakehouse SQL execution parity through the existing read-only MCP SQL contract**

## Performance

- **Duration:** 15m
- **Started:** 2026-04-10T16:10:00Z
- **Completed:** 2026-04-10T16:25:47Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Added structured Fabric SQL endpoint mapping configuration (`fabric_sql_endpoint_map`) with deterministic parsing and docs/template coverage.
- Replaced Phase-2 Fabric execution gate with target-aware connection resolution for onprem/fabric execution in shared query and metadata paths.
- Added regression tests for Fabric warehouse/lakehouse execution, database mismatch rejection, missing endpoint mapping failures, and metadata routing behavior.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Fabric SQL endpoint mapping settings and parsing** - `1827d46` (feat)
2. **Task 2: Implement target-aware onprem/fabric SQL execution core** - `d3e6b90` (feat)
3. **Task 3: Add parity regression coverage and finalize docs** - `7d73ea2` (test)

## Files Created/Modified

- `src/fde_sql_mcp/config.py` - Added `fabric_sql_endpoint_map` parsing and settings field.
- `src/fde_sql_mcp/clients/sql.py` - Added optional SQL-auth support (`username/password`) with trusted connection fallback.
- `src/fde_sql_mcp/tools/databases.py` - Added Fabric execution resolver and fail-closed endpoint mapping checks.
- `tests/test_settings_fabric.py` - Added endpoint-map parsing tests.
- `tests/test_target_routing.py` - Added Fabric execution and metadata parity regression tests.
- `fde_sql_mcp.config.template.json` - Added Fabric warehouse/lakehouse endpoint mapping examples.
- `README.md` - Updated configuration and behavior docs for phase-3 Fabric parity.

## Decisions Made

- Fabric execution requires explicit workspace+endpoint mapping entries; absent or invalid mappings return validation errors.
- For Fabric routes, tool `database` argument must match routed target database to prevent cross-context drift.
- Metadata tools now use the same target-aware execution path as `run_readonly_query`.

## Deviations from Plan

None - plan executed as written.

## Issues Encountered

None.

## User Setup Required

- Populate `fabric_sql_endpoint_map` (or `FABRIC_SQL_ENDPOINT_MAP`) with real Fabric Warehouse/Lakehouse SQL endpoint coordinates and credentials for allowlisted workspaces.

## Next Phase Readiness

- Phase 4 can harden cross-target guardrails and operator documentation on top of now-functional onprem/fabric query parity.

## Known Stubs

None.

## Self-Check: PASSED

FOUND: .planning/phases/03-fabric-sql-endpoint-parity/03-01-SUMMARY.md  
FOUND: 1827d46  
FOUND: d3e6b90  
FOUND: 7d73ea2
