---
phase: 02-target-routing-and-governance
plan: 01
subsystem: api
tags: [python, mcp, sql-server, routing, governance, fabric]
requires:
  - phase: 01-dual-target-foundation-and-auth
    provides: Fabric config/auth foundation and unchanged on-prem SQL tool contract
provides:
  - Deterministic active-target routing between onprem and fabric
  - Fabric workspace/database allowlist enforcement with optional workspace-ID mapping
  - Query response target context and additive target-management MCP tools
affects: [phase-3-fabric-sql, phase-4-guardrails]
tech-stack:
  added: []
  patterns: [centralized-target-router, additive-mcp-tools, context-aware-query-envelope]
key-files:
  created:
    - src/fde_sql_mcp/tools/targeting.py
    - tests/test_target_routing.py
  modified:
    - src/fde_sql_mcp/config.py
    - src/fde_sql_mcp/server.py
    - src/fde_sql_mcp/tools/databases.py
    - fde_sql_mcp.config.template.json
    - README.md
    - tests/test_settings_fabric.py
key-decisions:
  - "Routing is process-local state with explicit set/get tools and deterministic hint parsing."
  - "Fabric target resolution fails closed for ambiguous or out-of-allowlist workspace/database input."
  - "Existing SQL tools remain unchanged; target awareness is additive through routing tools and query context."
patterns-established:
  - "Route once, validate centrally: all target-governance logic lives in tools/targeting.py."
  - "Expose execution context in query responses via `target_context` to prevent environment ambiguity."
requirements-completed: [ROUTE-02, ROUTE-03, ROUTE-04, FAB-01, SAFE-03, CONF-02]
duration: 12m
completed: 2026-04-10
---

# Phase 2 Plan 01: Target Routing and Governance Summary

**Deterministic onprem/fabric target routing with allowlist governance and query response target context on the existing MCP SQL surface**

## Performance

- **Duration:** 12m
- **Started:** 2026-04-10T16:04:49Z
- **Completed:** 2026-04-10T16:16:30Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments
- Added a centralized routing module that supports explicit and natural-language target selection.
- Enforced Fabric workspace/database governance with allowlist checks and optional workspace-ID mappings.
- Added additive routing tools and query `target_context` output while keeping existing SQL tool signatures unchanged.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add deterministic target router and MCP tool wiring** - `40b6e1a` (feat)
2. **Task 2: Add target context to query results with governance-aware routing** - `6d0522a` (feat)
3. **Task 3: Add regression tests and update operator docs/template** - `5e9e658` (test)

## Files Created/Modified
- `src/fde_sql_mcp/tools/targeting.py` - Active-target state, deterministic resolution, allowlist governance, workspace discovery.
- `src/fde_sql_mcp/config.py` - Added workspace-ID mapping parsing (`fabric_workspace_id_map`).
- `src/fde_sql_mcp/server.py` - Added `set_query_target`, `get_query_target`, and `list_fabric_workspaces` MCP tools.
- `src/fde_sql_mcp/tools/databases.py` - Added onprem/fabric execution gate and `target_context` in query responses.
- `tests/test_target_routing.py` - Added phase-2 routing/governance/query-context coverage.
- `tests/test_settings_fabric.py` - Extended config parsing coverage for workspace-ID mappings.
- `fde_sql_mcp.config.template.json` - Added `fabric_workspace_id_map` template entries.
- `README.md` - Documented target-routing tools and phase-2/phase-3 execution boundary.

## Decisions Made
- Fabric target selection is accepted in phase 2 but query execution remains blocked until phase 3 endpoint parity.
- Natural-language resolution uses deterministic alias/token parsing with explicit ambiguity errors.
- Workspace IDs are only accepted when mapped to canonical allowlisted workspace names.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 3 can now wire Fabric Warehouse/Lakehouse SQL execution into the routing/governance layer built in phase 2.
- Remaining risk: Fabric execution is intentionally blocked in `run_readonly_query` until phase 3 implementation lands.

## Known Stubs

None.

---
*Phase: 02-target-routing-and-governance*
*Completed: 2026-04-10*

## Self-Check: PASSED
FOUND: .planning/phases/02-target-routing-and-governance/02-01-SUMMARY.md
FOUND: 40b6e1a
FOUND: 6d0522a
FOUND: 5e9e658
