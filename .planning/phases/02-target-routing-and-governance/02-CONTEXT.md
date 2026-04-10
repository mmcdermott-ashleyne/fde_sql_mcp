# Phase 2: Target Routing and Governance - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Add deterministic target routing and governance controls so users can explicitly or naturally select `onprem` vs `fabric`, while enforcing Fabric allowlists and surfacing resolved target context without changing the existing read-only SQL tool contract.

</domain>

<decisions>
## Implementation Decisions

### Target Selection UX
- **D-01:** Add explicit target-management MCP tools for runtime routing: one tool to set the active target and one tool to read it back.
- **D-02:** Support deterministic natural-language routing by accepting a single freeform target hint and resolving it into structured target context (`environment`, `workspace`, `endpoint_type`, `database`).
- **D-03:** Keep existing SQL/query tool names and signatures stable; routing should be additive and happen internally.

### Fabric Governance and Allowlist Enforcement
- **D-04:** Fabric workspace selection is restricted to an allowlisted workspace set and optional mapped workspace IDs; non-allowlisted selections are rejected.
- **D-05:** Fabric database selection is restricted to allowlisted SQL databases (initially `core_dw` and `core_lh`).
- **D-06:** Resolution must fail closed: if routing input is ambiguous or outside allowlist, return a clear validation error and do not mutate active target.

### Response Context and Operator Clarity
- **D-07:** Query responses include resolved target context so users can verify execution location.
- **D-08:** Add a dedicated tool to list allowed Fabric workspaces and mapped IDs so operators can discover valid targets without guessing.

### the agent's Discretion
- Exact parser heuristics for natural-language tokens (`dev/stg/prod`, `warehouse/lakehouse`) as long as they remain deterministic.
- Exact shape of runtime state container (module-level singleton vs small class), as long as thread-safe updates are preserved.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase and Requirement Contract
- `.planning/ROADMAP.md` — Phase 2 goal/success criteria and dependency on Phase 1.
- `.planning/REQUIREMENTS.md` — Required IDs: `ROUTE-02`, `ROUTE-03`, `ROUTE-04`, `FAB-01`, `SAFE-03`, `CONF-02`.
- `.planning/PROJECT.md` — Read-only and governance constraints.
- `AGENTS.md` — Project conventions and GSD workflow constraints.

### Existing Implementation Baseline
- `src/fde_sql_mcp/config.py` — Existing Fabric settings and allowlist inputs.
- `src/fde_sql_mcp/server.py` — MCP tool registration surface that should remain stable.
- `src/fde_sql_mcp/tools/databases.py` — Existing read-only query and metadata execution paths that need routing awareness.
- `src/fde_sql_mcp/tools/auth.py` — Existing diagnostics pattern to mirror for new target diagnostics.
- `README.md` — Tool contract documentation that must stay mostly unchanged while becoming target-aware.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Settings` in `src/fde_sql_mcp/config.py` already carries Fabric allowlist/default fields and is the right source for governance decisions.
- `run_readonly_query_impl` in `src/fde_sql_mcp/tools/databases.py` already centralizes query result shaping; target context can be appended there.

### Established Patterns
- MCP handlers in `server.py` are thin wrappers that delegate implementation to `tools/*_impl` functions.
- Runtime behavior is currently process-local and stateless per request; target routing can be implemented as controlled in-process state for this phase.

### Integration Points
- New routing helpers should live under `src/fde_sql_mcp/tools/` and be invoked from new MCP tool wrappers in `server.py`.
- Database/query tools should call a shared target-resolution helper before execution so governance checks are centralized.

</code_context>

<specifics>
## Specific Ideas

- Keep `onprem` as the default active target to preserve existing prompt flows.
- Resolve shorthand environment hints (`dev`, `stg`, `prod`) to canonical allowlisted workspace names.
- Prepare workspace ID mapping in config now so service-principal workflows can use stable IDs without bypassing allowlist checks.

</specifics>

<deferred>
## Deferred Ideas

- Actual Fabric Warehouse/Lakehouse SQL endpoint query execution (Phase 3).
- Cross-target unified guardrail hardening and full operator documentation pass (Phase 4).

</deferred>

---

*Phase: 02-target-routing-and-governance*
*Context gathered: 2026-04-10*
