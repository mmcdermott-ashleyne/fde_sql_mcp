# Phase 3: Fabric SQL Endpoint Parity - Research

**Researched:** 2026-04-10
**Domain:** Target-aware SQL execution path for on-prem and Fabric Warehouse/Lakehouse endpoints
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Shared SQL MCP tool contract is preserved (no Fabric-specific query tool fork).
- Fabric execution is explicitly configured and allowlist-governed.
- Metadata helpers should run target-aware across on-prem/Fabric where supported.
- Scope stays SQL-only.

### the agent's Discretion
- Endpoint mapping schema details.
- Internal helper boundaries for connection/auth selection.

</user_constraints>

<research_summary>
## Summary

Phase 2 introduced deterministic target selection but intentionally blocks Fabric execution. Phase 3 should remove that gate by adding an execution-path resolver that maps Fabric target context to configured SQL endpoint coordinates and then uses the existing read-only query/metadata helpers unchanged at the tool surface.

Given current architecture, the lowest-risk approach is:
1. Add Fabric endpoint mapping settings in `config.py`.
2. Extend SQL connection client to support both Windows auth (on-prem) and SQL auth (Fabric endpoint user/password or token-ready pattern).
3. Route `_fetch_rows` and `run_readonly_query_impl` through one target-aware resolver in `databases.py`.
4. Extend tests/docs to verify warehouse/lakehouse parity and SQL-only behavior.

This satisfies `FAB-02`..`FAB-05` and `SAFE-04` while preserving existing contracts.
</research_summary>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: Target-Aware Connection Resolution
Resolve runtime connection params from active target context and settings before any query execution.

### Pattern 2: Shared Execution Core
Keep one `_fetch_rows` and one `run_readonly_query_impl`; only connection selection changes by target.

### Pattern 3: Explicit Endpoint Mapping
Require config-supplied Fabric SQL endpoint mappings by workspace+endpoint type; fail closed when missing.

</architecture_patterns>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Silent fallback to on-prem when Fabric mapping is missing
**Mitigation:** Raise explicit validation error; never substitute on-prem.

### Pitfall 2: Endpoint/database mismatch (`warehouse` with `core_lh`)
**Mitigation:** Validate compatibility before connecting.

### Pitfall 3: Accidental scope expansion into non-SQL Fabric APIs
**Mitigation:** No new non-SQL MCP tool surface; keep all operations SQL via ODBC.

</common_pitfalls>

<sources>
## Sources

- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/phases/02-target-routing-and-governance/02-CONTEXT.md`
- `src/fde_sql_mcp/config.py`
- `src/fde_sql_mcp/tools/targeting.py`
- `src/fde_sql_mcp/tools/databases.py`
- `src/fde_sql_mcp/clients/sql.py`

</sources>

---

*Phase: 03-fabric-sql-endpoint-parity*
*Research completed: 2026-04-10*
*Ready for planning: yes*
