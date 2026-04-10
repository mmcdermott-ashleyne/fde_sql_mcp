# Phase 1: Dual-Target Foundation and Auth - Research

**Researched:** 2026-04-10
**Domain:** Python MCP server configuration and Fabric authentication foundations
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Keep one shared runtime settings object and extend it with Fabric-specific fields while preserving existing on-prem defaults and env var names.
- Prefer client-secret Fabric auth when `FABRIC_TENANT_ID`, `FABRIC_CLIENT_ID`, and `FABRIC_CLIENT_SECRET` are all configured.
- Fallback to browser-capable/default auth mode when any client-secret variable is missing; startup must stay non-blocking.
- Keep Phase 1 additive and internal: no breaking tool contract changes and no scope pull-in from routing phases.

### the agent's Discretion
- Internal helper/module boundaries for Fabric auth resolution.
- Exact structure of auth diagnostics payload returned to tools.

### Deferred Ideas (OUT OF SCOPE)
- Explicit on-prem/fabric target routing commands.
- Natural-language target resolution.
- Fabric endpoint execution and allowlist enforcement logic.

</user_constraints>

<research_summary>
## Summary

The current codebase already uses a centralized immutable settings model with helper parsing functions and one connection abstraction per backend family. The safest Phase 1 implementation is to preserve that shape and add Fabric foundation fields and auth-resolution logic without introducing runtime dependencies on active Fabric operations.

A deterministic auth-mode selector should be pure and side-effect free: compute mode from resolved settings, expose a structured diagnostic output, and keep startup behavior permissive. This supports `AUTH-01` through `AUTH-03` now while deferring real Fabric endpoint usage to later phases.

**Primary recommendation:** Add Fabric config + auth mode resolution + diagnostics tool, then pin behavior with focused unit tests to guarantee on-prem compatibility.
</research_summary>

<architecture_patterns>
## Architecture Patterns

### Pattern 1: Additive Settings Expansion
**What:** Extend `Settings` dataclass in `src/fde_sql_mcp/config.py` with Fabric fields and small normalization helpers.
**When to use:** Anytime new runtime knobs are introduced.
**Why:** Keeps one source of truth and minimizes callsite churn.

### Pattern 2: Pure Auth Resolver
**What:** Implement Fabric auth decision logic as pure functions over settings (no network calls).
**When to use:** Early foundation phases where deterministic behavior matters more than active service calls.
**Why:** Makes precedence and fallback behavior testable without credentials.

### Pattern 3: Thin MCP Tool Wrapper
**What:** Add a read-only diagnostics tool in `server.py` that delegates to implementation helpers.
**When to use:** Exposing internal runtime state safely.
**Why:** Matches existing server/tool layering conventions.

</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Config parsing behavior | Ad-hoc per-field parsing in multiple files | Existing `_local_setting`, `_get_bool`, `_get_int` patterns in `config.py` | Prevents precedence drift and parsing bugs |
| Auth diagnostics endpoint shape | One-off inline payload in server layer | Typed helper payload in tool implementation | Keeps logic centralized and testable |

**Key insight:** Phase 1 success is mostly deterministic behavior and compatibility, not network integration.
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Breaking on-prem defaults while adding Fabric fields
**What goes wrong:** Existing SQL settings behavior changes unexpectedly.
**How to avoid:** Keep existing defaults and env var names untouched; add new fields only.

### Pitfall 2: Non-deterministic auth precedence
**What goes wrong:** Partial client-secret config still attempts service-principal flow.
**How to avoid:** Require all three client-secret env values before selecting client-secret mode.

### Pitfall 3: Startup hard-fail on optional Fabric config
**What goes wrong:** Server cannot start in on-prem-only workflows.
**How to avoid:** Treat Fabric config as optional foundation in this phase; diagnostics should report mode, not fail startup.
</common_pitfalls>

## Validation Architecture

Phase 1 validation should be test-first around configuration and auth-mode resolution:
- Unit tests for precedence (`client_secret` vs fallback).
- Unit tests for single-tenant context resolution.
- Regression tests for existing SQL defaults in `Settings`.
- Lightweight sanity checks for new diagnostics payload shape.

<sources>
## Sources

### Primary (HIGH confidence)
- `.planning/ROADMAP.md` — Phase 1 goals and success criteria.
- `.planning/REQUIREMENTS.md` — Requirement IDs and exact acceptance intent.
- `src/fde_sql_mcp/config.py` — existing configuration precedence behavior.
- `src/fde_sql_mcp/server.py` and `src/fde_sql_mcp/tools/databases.py` — existing tool delegation pattern.

</sources>

<metadata>
## Metadata

**Research scope:**
- Core technology: Python MCP + runtime settings/auth-mode resolution.
- Patterns: additive config extension, pure decision functions, tool diagnostics.
- Pitfalls: compatibility regressions, auth precedence ambiguity.

**Research date:** 2026-04-10
**Valid until:** 2026-05-10
</metadata>

---

*Phase: 01-dual-target-foundation-and-auth*
*Research completed: 2026-04-10*
*Ready for planning: yes*
