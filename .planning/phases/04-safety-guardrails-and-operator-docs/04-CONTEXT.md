# Phase 4: Safety Guardrails and Operator Docs - Context

**Gathered:** 2026-04-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Enforce consistent read-only query guardrails across on-prem and Fabric execution paths and document operator setup/usage for dual-environment routing.

</domain>

<decisions>
## Implementation Decisions

### Cross-Target Read-Only Enforcement
- **D-01:** Keep one shared read-only validator and enforce it before query execution regardless of active target (`onprem` or `fabric`).
- **D-02:** Block multi-statement payloads and disallowed write/procedure keywords identically for both targets.
- **D-03:** Keep `sql_enforce_readonly` as the single feature flag controlling validator enablement across both targets.

### Guardrail Consistency
- **D-04:** Apply the same max query length (`sql_max_query_chars`) and timeout (`sql_query_timeout`) behavior to both `run_readonly_query_impl` and metadata helper execution paths.
- **D-05:** Enforce row limits uniformly by clamping requested `max_rows` to `sql_max_rows` and exposing `row_limit` + `truncated` in responses.
- **D-06:** Add regression tests that prove guardrail behavior is target-agnostic for on-prem and Fabric routes.

### Operator Documentation
- **D-07:** Expand README with dual-environment setup flow covering auth precedence, endpoint mapping, and allowlist expectations.
- **D-08:** Add explicit copy/paste examples for target switching via both explicit syntax and natural-language hints.
- **D-09:** Document expected guardrail validation failures so operators can distinguish safety rejections from connectivity issues.

### the agent's Discretion
- Exact test fixture layout for cross-target guardrail coverage.
- Exact README section names and ordering while keeping current tool semantics and scope.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Contract
- `.planning/ROADMAP.md` — Phase 4 goal, requirements, and success criteria.
- `.planning/REQUIREMENTS.md` — Requirement IDs `SAFE-01`, `SAFE-02`, `CONF-03`.
- `.planning/STATE.md` — Current phase position and prior decisions.

### Prior-Phase Baseline
- `.planning/phases/03-fabric-sql-endpoint-parity/03-CONTEXT.md` — Locked routing/execution decisions Phase 4 must preserve.
- `.planning/phases/03-fabric-sql-endpoint-parity/03-01-SUMMARY.md` — Implemented Fabric parity behavior and known follow-up into Phase 4.

### Implementation and Docs Surfaces
- `src/fde_sql_mcp/tools/databases.py` — Read-only validation, row limiting, timeout handling, and target execution path.
- `src/fde_sql_mcp/tools/targeting.py` — Routing context model used by shared execution path.
- `README.md` — Operator documentation surface for setup and routing usage.
- `fde_sql_mcp.config.template.json` — Published dual-environment config model.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_validate_readonly_query` in `src/fde_sql_mcp/tools/databases.py` already centralizes keyword and multi-statement validation.
- `_normalize_max_rows` in `src/fde_sql_mcp/tools/databases.py` already enforces hard row caps.
- `_resolve_execution_target` in `src/fde_sql_mcp/tools/databases.py` already unifies on-prem/Fabric connection routing.

### Established Patterns
- Tool handlers in `server.py` are thin async wrappers and should stay unchanged for this phase.
- Runtime guardrails are config-driven through `Settings` in `config.py`.

### Integration Points
- Extend tests in `tests/test_target_routing.py` for cross-target guardrail parity.
- Add focused unit coverage for query validator behavior in a dedicated test module.
- Update README and config template documentation sections without changing MCP tool signatures.

</code_context>

<specifics>
## Specific Ideas

- Keep the UX lean: no new MCP tools; strengthen behavior and docs around existing tools only.
- Make docs explicit about the safe way to switch environments before running queries.

</specifics>

<deferred>
## Deferred Ideas

- Dedicated diagnostics/audit logging enhancements (`OPS-01`, `OPS-02`) remain future milestone scope.
- Metadata caching/performance optimization (`PERF-01`) remains out of this phase.

</deferred>

---

*Phase: 04-safety-guardrails-and-operator-docs*
*Context gathered: 2026-04-13*
