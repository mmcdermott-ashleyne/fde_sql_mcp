# Phase 2: Target Routing and Governance - Research

**Researched:** 2026-04-10
**Domain:** MCP target routing, allowlist governance, and query context propagation
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Add explicit target-management tools while preserving existing SQL tool names/signatures.
- Support deterministic natural-language target resolution.
- Enforce Fabric workspace/database allowlists with fail-closed behavior.
- Include resolved target context in query responses.

### the agent's Discretion
- Target-hint parsing heuristics and ambiguity handling.
- Internal runtime state structure for active target management.

### Deferred Ideas (OUT OF SCOPE)
- Fabric SQL endpoint execution parity (Phase 3).
- Cross-target safety harmonization and full operator docs pass (Phase 4).

</user_constraints>

<research_summary>
## Summary

Phase 2 should introduce a dedicated routing layer under `tools/` that owns active-target state, target-hint parsing, allowlist checks, and context payload construction. Existing SQL query tools should remain callable with the same parameters and delegate to this routing layer to report resolved context and enforce governance checks before execution.

To satisfy FAB-01 and SAFE-03 without Fabric execution yet, workspace/database selection should validate against configured allowlists and optional workspace ID mapping. If target resolution is ambiguous or out-of-allowlist, the router should return a deterministic validation error and avoid mutating active state.

**Primary recommendation:** Add a target router module, wire target tools in `server.py`, append `target_context` to `run_readonly_query` results, and codify behavior with focused unit tests.
</research_summary>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: Centralized Target Router
**What:** New `tools/targeting.py` module to resolve/set/get target context and validate allowlists.
**Why:** Keeps routing/governance logic out of MCP wrappers and DB execution helpers.

### Pattern 2: Additive Tool Surface
**What:** Add routing tools (`set_query_target`, `get_query_target`, `list_fabric_workspaces`) without renaming/removing existing SQL tools.
**Why:** Meets CONF-02 and protects existing prompt contracts.

### Pattern 3: Query Response Context Envelope
**What:** Keep existing `run_readonly_query` shape but add a `target_context` object.
**Why:** Satisfies ROUTE-04 while preserving backward compatibility.

</architecture_patterns>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Ambiguous natural-language routing
**Risk:** `fabric prod` may resolve differently across runs.
**Mitigation:** Deterministic token precedence + explicit ambiguity errors.

### Pitfall 2: Hidden allowlist bypass
**Risk:** Workspace IDs bypass name checks.
**Mitigation:** Resolve IDs through explicit configured map, then re-check canonical workspace against allowlist.

### Pitfall 3: Silent context drift
**Risk:** Query executes on on-prem while response implies Fabric.
**Mitigation:** Build `target_context` from the same resolved object used to route execution.

</common_pitfalls>

## Validation Architecture

Validation should focus on deterministic routing and governance:
- Unit tests for explicit and natural-language routing resolution.
- Unit tests for allowlist rejection and ID mapping enforcement.
- Unit test asserting `run_readonly_query` includes `target_context` for on-prem execution.
- Regression tests for existing on-prem behavior and unchanged tool signatures.

<sources>
## Sources

- `.planning/ROADMAP.md` — Phase 2 scope and success criteria.
- `.planning/REQUIREMENTS.md` — Requirement IDs and governance expectations.
- `src/fde_sql_mcp/config.py` — Existing allowlist/default Fabric config model.
- `src/fde_sql_mcp/server.py` — MCP tool wiring conventions.
- `src/fde_sql_mcp/tools/databases.py` — Query execution return envelope and read-only guardrails.

</sources>

---

*Phase: 02-target-routing-and-governance*
*Research completed: 2026-04-10*
*Ready for planning: yes*
