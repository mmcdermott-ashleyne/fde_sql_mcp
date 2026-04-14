---
phase: 04-safety-guardrails-and-operator-docs
plan: 01
subsystem: api
tags: [python, mcp, sql-server, fabric, guardrails, docs]
requires:
  - phase: 03-fabric-sql-endpoint-parity
    provides: Shared onprem/fabric SQL execution path and target routing context
provides:
  - Cross-target read-only and guardrail parity regression coverage
  - Unified timeout helper for query and metadata SQL execution paths
  - Operator guide for dual-environment setup, auth precedence, and routing usage
affects: [phase-5-ops-diagnostics, phase-5-performance]
tech-stack:
  added: []
  patterns: [cross-target-guardrail-parity-tests, shared-timeout-helper, operator-playbook-in-readme]
key-files:
  created:
    - tests/test_query_guardrails.py
  modified:
    - src/fde_sql_mcp/tools/databases.py
    - tests/test_target_routing.py
    - README.md
key-decisions:
  - "Guardrail parity is verified by executing the same read-only constraints under both on-prem and Fabric target contexts."
  - "Cursor timeout assignment is centralized to a shared helper to prevent drift between query and metadata code paths."
  - "Dual-environment operational guidance remains in the README as the canonical operator surface."
patterns-established:
  - "Target-aware tests should assert behavior parity, not just target-specific success paths."
  - "Documentation updates should include both explicit and natural-language route selection examples."
requirements-completed: [SAFE-01, SAFE-02, CONF-03]
duration: 2m
completed: 2026-04-13
---

# Phase 4 Plan 01: Safety Guardrails and Operator Docs Summary

**Cross-target read-only guardrail parity is regression-protected and documented with a dual-environment operator guide**.

## Performance

- **Duration:** 2m
- **Started:** 2026-04-13T20:56:44-04:00
- **Completed:** 2026-04-13T20:58:05-04:00
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Added dedicated guardrail tests that validate read-only rejection, max-query-length checks, row-limit clamping, and timeout handling across on-prem and Fabric targets.
- Refactored timeout assignment into a shared helper and applied it consistently in query and metadata execution paths.
- Expanded README with a practical operator guide for dual-environment setup, auth precedence, explicit/natural routing examples, and expected guardrail failures.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add cross-target guardrail regression coverage** - `e50d3f8` (test)
2. **Task 2: Harden shared timeout application in execution core** - `8027f3e` (refactor)
3. **Task 3: Expand operator docs for dual-environment safety and routing** - `9b1e2f1` (chore)

## Files Created/Modified

- `tests/test_query_guardrails.py` - New cross-target guardrail test coverage for SAFE-01 and SAFE-02.
- `tests/test_target_routing.py` - Added Fabric-target regression for write-query rejection.
- `src/fde_sql_mcp/tools/databases.py` - Added `_apply_cursor_timeout` helper and reused it across execution paths.
- `README.md` - Added operator guide for setup, routing, and safety expectations.

## Decisions Made

- Preserve existing MCP SQL tool surface and validate phase outcomes through behavior/tests/docs rather than new tool additions.
- Keep timeout application fail-safe for pyodbc variants that do not expose `cursor.timeout`.
- Document safety failure modes explicitly so operators can separate validation failures from routing/configuration failures.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- One test initially asserted the wrong failure branch because the query exceeded the configured max-query-length before hitting the non-read-only check; fixed by using a short non-SELECT payload.

## User Setup Required

None - no new runtime configuration values were introduced.

## Next Phase Readiness

- Phase 4 safety/documentation requirements are now covered by automated tests and operator docs.
- Future OPS/PERF phases can build on these guardrails without changing query tool semantics.

## Known Stubs

None.

## Self-Check: PASSED

FOUND: .planning/phases/04-safety-guardrails-and-operator-docs/04-01-SUMMARY.md  
FOUND: e50d3f8  
FOUND: 8027f3e  
FOUND: 9b1e2f1
