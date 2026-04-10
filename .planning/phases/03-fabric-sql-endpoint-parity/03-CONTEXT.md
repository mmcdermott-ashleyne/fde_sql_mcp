# Phase 3: Fabric SQL Endpoint Parity - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Enable read-only SQL execution against allowlisted Fabric Warehouse/Lakehouse SQL endpoints while keeping the existing MCP SQL tool surface and routing semantics introduced in Phase 2.

</domain>

<decisions>
## Implementation Decisions

### Fabric SQL Execution Contract
- **D-01:** Keep existing SQL/metadata MCP tool names and parameters unchanged; Fabric parity is implemented behind the same tool contract.
- **D-02:** Route execution by current active target (`onprem` or `fabric`) and use Fabric endpoint connection metadata only when `environment=fabric`.
- **D-03:** Enforce endpoint/database compatibility (`warehouse -> core_dw`, `lakehouse -> core_lh`) and reject mismatches before connecting.

### Fabric Connection Configuration
- **D-04:** Add explicit allowlisted Fabric SQL endpoint connection mappings in config by workspace and endpoint type to avoid implicit endpoint discovery at runtime.
- **D-05:** Fabric execution remains SQL-only over ODBC; no Fabric non-SQL APIs/tools are introduced.

### Metadata Tool Behavior
- **D-06:** Existing metadata discovery helpers run through the same target-aware connection path so they work on both on-prem and Fabric where endpoint SQL metadata supports them.
- **D-07:** Keep `target_context` in `run_readonly_query` responses so operators can verify execution location.

### the agent's Discretion
- Exact config key structure for Fabric endpoint mappings as long as it is deterministic and documented.
- Exact helper boundaries for connection resolution in `databases.py` and `clients/sql.py`.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Contract
- `.planning/ROADMAP.md` — Phase 3 goal, dependencies, and success criteria.
- `.planning/REQUIREMENTS.md` — Requirement IDs: `FAB-02`, `FAB-03`, `FAB-04`, `FAB-05`, `SAFE-04`.
- `.planning/STATE.md` — Current execution position and prior decisions.

### Existing Implementation Baseline
- `.planning/phases/02-target-routing-and-governance/02-CONTEXT.md` — Routing/governance decisions to preserve.
- `.planning/phases/02-target-routing-and-governance/02-01-SUMMARY.md` — Current behavior and explicit phase-3 execution gap.
- `src/fde_sql_mcp/tools/targeting.py` — Active target resolution and allowlist enforcement.
- `src/fde_sql_mcp/tools/databases.py` — Existing SQL and metadata execution path currently gated to on-prem.
- `src/fde_sql_mcp/clients/sql.py` — ODBC connection string and lifecycle management.
- `src/fde_sql_mcp/config.py` — Runtime settings model and parsing helpers.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `targeting.get_query_target_impl()` already returns canonical execution context (`environment`, `workspace`, `endpoint_type`, `database`).
- `_fetch_rows` and `run_readonly_query_impl` already centralize execution and can be upgraded to target-aware connection selection.

### Established Patterns
- `server.py` handlers remain thin and delegate to `tools/*_impl`.
- Connection creation is encapsulated in `clients/sql.py`.

### Integration Points
- Add Fabric endpoint mapping config fields in `Settings`.
- Add target-aware connection resolution helper(s) in `databases.py`, optionally extending `clients/sql.py` for auth mode support.
- Extend tests in `tests/test_target_routing.py` and `tests/test_settings_fabric.py`.

</code_context>

<specifics>
## Specific Ideas

- Keep allowlist restrictions as the only valid Fabric workspace/database surface.
- Continue default active target as `onprem`.
- Return explicit validation errors when Fabric endpoint mapping is missing or incomplete.

</specifics>

<deferred>
## Deferred Ideas

- Fabric pipeline/notebook orchestration (out of scope for this SQL-only MCP).
- Cross-target guardrail hardening and broad doc pass remains Phase 4 scope.

</deferred>

---

*Phase: 03-fabric-sql-endpoint-parity*
*Context gathered: 2026-04-10*
