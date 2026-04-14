# Phase 4: Safety Guardrails and Operator Docs - Research

**Researched:** 2026-04-13
**Domain:** Cross-target read-only safety parity and operator-facing dual-environment documentation
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Keep one shared read-only validator path and enforce it for both on-prem and Fabric execution.
- Enforce timeout/row/query-length guardrails consistently regardless of active target.
- Do not add new MCP tools; improve safety behavior and documentation around existing tools.
- Provide explicit and natural-language routing examples in operator docs.

### the agent's Discretion
- Exact test module and fixture structure for guardrail coverage.
- README section organization and wording details.

</user_constraints>

<research_summary>
## Summary

Phase 3 introduced target-aware on-prem/Fabric SQL execution parity through a shared execution core in `databases.py`. Guardrail logic is already centralized (`_validate_readonly_query`, `_normalize_max_rows`, timeout assignment). Phase 4 should harden this by adding regression coverage that proves identical behavior under both targets and improving operator docs for setup and usage.

Lowest-risk implementation sequence:
1. Add tests that assert read-only validation, row limits, and timeout behavior under both `onprem` and `fabric` contexts.
2. Apply a small refactor to eliminate duplicated timeout assignment and keep behavior uniform between query and metadata execution paths.
3. Expand README with a dual-environment runbook (auth precedence, configuration checklist, explicit/natural routing examples, and safety failure expectations).

This satisfies `SAFE-01`, `SAFE-02`, and `CONF-03` while preserving the existing MCP tool surface.
</research_summary>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: One Validator, Multiple Targets
Use `_validate_readonly_query` once in `run_readonly_query_impl` before any target-specific execution.

### Pattern 2: Shared Guardrail Helpers
Apply common helper logic (`_normalize_max_rows`, timeout assignment) before sending SQL to the selected backend.

### Pattern 3: Operator Docs in Primary README Surface
Keep setup and usage guidance in one canonical doc (`README.md`) to reduce drift.

</architecture_patterns>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Target-specific drift in guardrails
**Mitigation:** Add regression tests that execute the same query flow against both target contexts and compare guardrail outputs.

### Pitfall 2: Timeout behavior silently diverging across code paths
**Mitigation:** Consolidate timeout assignment in one helper used by both query and metadata execution.

### Pitfall 3: Operator confusion between routing errors and safety rejections
**Mitigation:** Document representative validation failures and the expected remediation path.

</common_pitfalls>

<sources>
## Sources

- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/phases/04-safety-guardrails-and-operator-docs/04-CONTEXT.md`
- `.planning/phases/03-fabric-sql-endpoint-parity/03-CONTEXT.md`
- `src/fde_sql_mcp/tools/databases.py`
- `src/fde_sql_mcp/tools/targeting.py`
- `README.md`

</sources>

---

*Phase: 04-safety-guardrails-and-operator-docs*
*Research completed: 2026-04-13*
*Ready for planning: yes*
