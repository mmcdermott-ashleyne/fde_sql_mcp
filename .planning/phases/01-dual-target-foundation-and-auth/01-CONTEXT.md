# Phase 1: Dual-Target Foundation and Auth - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the dual-target configuration and Fabric authentication foundation so the server can carry both on-prem and Fabric settings without breaking current on-prem tool behavior.

</domain>

<decisions>
## Implementation Decisions

### Configuration Model
- **D-01:** Keep one shared runtime settings object and extend it with Fabric-specific fields (tenant/client/auth/allowlist), while preserving existing on-prem SQL defaults and env var names.
- **D-02:** Continue loading local JSON first and environment overrides second, so existing local `fde_sql_mcp.config.json` usage remains valid.

### Fabric Authentication Behavior
- **D-03:** Select Fabric client-secret mode when `FABRIC_TENANT_ID`, `FABRIC_CLIENT_ID`, and `FABRIC_CLIENT_SECRET` are all present.
- **D-04:** If any client-secret variable is missing, select browser-capable fallback auth mode and do not fail server startup.
- **D-05:** Treat Fabric auth as single-tenant and bind all Fabric auth decisions to one resolved tenant context.

### Compatibility and Safety Baseline
- **D-06:** Preserve current on-prem connection behavior and existing MCP tool signatures in this phase; Fabric foundations are internal and additive.
- **D-07:** Add explicit auth diagnostics data structures/functions now so future Fabric routing tools can expose auth mode without refactoring.

### the agent's Discretion
- Exact internal module/file split for Fabric auth helpers.
- Whether allowlist defaults are embedded constants or pulled only from config.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase and Requirements
- `.planning/ROADMAP.md` — Phase 1 goal, scope, and success criteria.
- `.planning/REQUIREMENTS.md` — Phase requirement IDs `ROUTE-01`, `AUTH-01`, `AUTH-02`, `AUTH-03`, `CONF-01`.
- `.planning/PROJECT.md` — Core value and constraints for dual-target read-only behavior.
- `AGENTS.md` — Project constraints and workflow requirements.

### Existing Implementation Baseline
- `src/fde_sql_mcp/config.py` — Current settings loader and env precedence pattern.
- `src/fde_sql_mcp/clients/sql.py` — Existing SQL connection abstraction to preserve for on-prem.
- `README.md` — Current documented setup/behavior that must remain valid.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Settings` dataclass in `src/fde_sql_mcp/config.py`: central runtime configuration object suitable for additive Fabric fields.
- `_get_bool`, `_get_int`, `_local_setting` helpers in `src/fde_sql_mcp/config.py`: reusable parsing patterns for new Fabric config keys.

### Established Patterns
- Runtime settings are process-wide immutable (`settings = Settings()`), so new Fabric behavior should be resolved up front and exposed read-only.
- DB connectivity is encapsulated in client modules (`src/fde_sql_mcp/clients/`), making a dedicated Fabric auth helper module consistent with architecture.

### Integration Points
- Add Fabric auth mode resolution to config layer and consume from future Fabric SQL client/routing layers.
- Keep server/tool contract unchanged in Phase 1; only foundational internals and diagnostics are introduced.

</code_context>

<specifics>
## Specific Ideas

- Client-secret precedence is non-negotiable when all required secrets are configured.
- Fallback mode must be browser-capable and non-blocking at startup to support local/dev workflows.
- Keep prompt/tool ergonomics stable while enabling future target routing work.

</specifics>

<deferred>
## Deferred Ideas

- Explicit environment switching commands and natural-language routing (Phase 2).
- Fabric Warehouse/Lakehouse SQL endpoint execution paths (Phase 3).
- Cross-target runtime read-only guardrail harmonization and operator docs expansion (Phase 4).

</deferred>

---

*Phase: 01-dual-target-foundation-and-auth*
*Context gathered: 2026-04-10*
