---
phase: 01-dual-target-foundation-and-auth
plan: 01
subsystem: api
tags: [python, mcp, sql-server, fabric, auth]
requires:
  - phase: 0
    provides: Existing on-prem SQL MCP tool surface
provides:
  - Unified dual-target runtime settings model for on-prem and Fabric foundation
  - Deterministic Fabric auth mode precedence with single-tenant context resolution
  - Non-secret auth diagnostics MCP tool (`get_auth_info`)
affects: [phase-2-routing, phase-3-fabric-sql, phase-4-guardrails]
tech-stack:
  added: [pytest]
  patterns: [additive-settings-expansion, pure-auth-mode-resolution, thin-mcp-tool-delegation]
key-files:
  created:
    - src/fde_sql_mcp/tools/auth.py
    - tests/test_settings_fabric.py
  modified:
    - src/fde_sql_mcp/config.py
    - src/fde_sql_mcp/server.py
    - fde_sql_mcp.config.template.json
    - README.md
key-decisions:
  - "Keep existing on-prem SQL behavior unchanged while adding Fabric config/auth fields."
  - "Resolve Fabric auth mode deterministically: client_secret only when all three secret inputs are present."
  - "Expose auth diagnostics without returning any secret values."
patterns-established:
  - "Foundation-first Fabric rollout: config + diagnostics before routing/execution."
  - "Test auth precedence with pure settings construction and monkeypatched config state."
requirements-completed: [ROUTE-01, AUTH-01, AUTH-02, AUTH-03, CONF-01]
duration: 4m
completed: 2026-04-10
---

# Phase 1 Plan 01: Dual-Target Foundation and Auth Summary

**Dual-target settings and deterministic Fabric auth mode foundation with non-secret diagnostics on the existing MCP surface**

## Performance

- **Duration:** 4m
- **Started:** 2026-04-10T15:39:31Z
- **Completed:** 2026-04-10T15:43:45Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- Extended runtime settings to include Fabric foundation fields and derived auth mode/tenant context.
- Added `get_auth_info` MCP tool backed by dedicated auth diagnostics implementation.
- Added Phase 1 regression/unit coverage and updated template/docs for dual-target configuration and auth precedence.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend runtime settings for dual-target foundation** - `6695272` (feat)
2. **Task 2: Add auth diagnostics implementation and MCP tool wiring** - `18a1706` (feat)
3. **Task 3: Document and test Phase 1 behavior contract** - `582d58e` (test)

## Files Created/Modified
- `src/fde_sql_mcp/config.py` - Added Fabric config fields, auth-mode resolution, and tenant-context derivation.
- `src/fde_sql_mcp/tools/auth.py` - Added non-secret auth diagnostics payload builder.
- `src/fde_sql_mcp/server.py` - Added MCP `get_auth_info` tool delegation.
- `tests/test_settings_fabric.py` - Added coverage for SQL defaults, Fabric auth precedence/fallback, and diagnostics secrecy.
- `fde_sql_mcp.config.template.json` - Added Fabric settings and allowlist defaults.
- `README.md` - Documented Fabric env/config keys and deterministic auth precedence.

## Decisions Made
- Implemented auth mode as deterministic derived state (`fabric_auth_mode`) rather than ad-hoc runtime branching.
- Kept Fabric diagnostics strictly non-secret with boolean presence indicators.
- Fixed local config path resolution to repository root so documented local config behavior is actually honored.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed local config path resolution**
- **Found during:** Task 1
- **Issue:** `config.py` looked for `fde_sql_mcp.config.json` under `src/` instead of repository root.
- **Fix:** Updated `_CONFIG_PATH` to repo root (`parents[2]`) and preserved existing load semantics.
- **Files modified:** `src/fde_sql_mcp/config.py`
- **Verification:** `Settings()` correctly loaded root config and tests passed.
- **Committed in:** `6695272`

**2. [Rule 3 - Blocking] Installed missing pytest in venv for test verification**
- **Found during:** Task 3
- **Issue:** `.venv` had no `pytest`, blocking required verification command.
- **Fix:** Installed `pytest` in local venv (`python -m pip install pytest`).
- **Files modified:** none (environment-only)
- **Verification:** `.venv\Scripts\python -m pytest -q` returned `7 passed`.
- **Committed in:** N/A (no repo file changes)

---

**Total deviations:** 2 auto-fixed (Rule 1: 1, Rule 3: 1)
**Impact on plan:** Both were required to make planned behavior and verification actually work; no scope creep introduced.

## Issues Encountered
- Missing local `pytest` dependency in the active virtual environment. Resolved by installing it before executing plan verification.

## User Setup Required

None - no external service configuration required for this phase.

## Next Phase Readiness
- Phase 1 foundations are in place for Phase 2 routing/governance work.
- Remaining risk: Fabric auth mode is foundational only; actual token acquisition/execution path is still deferred to upcoming phases.

## Known Stubs

None.

---
*Phase: 01-dual-target-foundation-and-auth*
*Completed: 2026-04-10*

## Self-Check: PASSED
FOUND: .planning/phases/01-dual-target-foundation-and-auth/01-01-SUMMARY.md
FOUND: 6695272
FOUND: 18a1706
FOUND: 582d58e

