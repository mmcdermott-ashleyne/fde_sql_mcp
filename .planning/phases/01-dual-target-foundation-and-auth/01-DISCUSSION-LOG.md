# Phase 1: Dual-Target Foundation and Auth - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-10T16:30:00Z
**Phase:** 1-Dual-Target Foundation and Auth
**Areas discussed:** Configuration model, Fabric auth precedence, Tenant handling, Compatibility boundary

---

## Configuration model

| Option | Description | Selected |
|--------|-------------|----------|
| Extend current `Settings` with Fabric fields | Keep one unified runtime config surface for on-prem + Fabric | ✓ |
| Add separate Fabric config object | Independent config object and loader path | |
| Environment-only Fabric config | Do not allow Fabric JSON keys in local config | |

**User's choice:** Extend current `Settings` with Fabric fields (auto default)
**Notes:** Auto mode selected additive approach to avoid breaking existing config semantics.

---

## Fabric auth precedence

| Option | Description | Selected |
|--------|-------------|----------|
| Client-secret first, fallback if incomplete | Prefer deterministic service principal auth and degrade gracefully | ✓ |
| Always use default/browser auth | Simpler implementation but loses explicit service principal path | |
| Fail startup if client-secret vars are incomplete | Strict but blocks local workflows | |

**User's choice:** Client-secret first, fallback if incomplete (auto default)
**Notes:** Matches recorded project decision and Phase 1 success criteria.

---

## Tenant handling

| Option | Description | Selected |
|--------|-------------|----------|
| Single resolved tenant context | One Fabric tenant used for all allowlisted environments | ✓ |
| Multi-tenant by workspace | Choose tenant per workspace | |
| Tenant-agnostic mode | Defer tenant checks until query time | |

**User's choice:** Single resolved tenant context (auto default)
**Notes:** Aligns with project constraint and `AUTH-03`.

---

## Compatibility boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve current on-prem behavior exactly | Add Fabric internals without tool contract changes | ✓ |
| Start introducing target-routing tools now | Partial scope pull-in from Phase 2 | |
| Replace SQL client abstraction immediately | Larger architecture shift in Phase 1 | |

**User's choice:** Preserve current on-prem behavior exactly (auto default)
**Notes:** Avoids scope creep and keeps `ROUTE-01` stable.

---

## the agent's Discretion

- Internal naming and file partitioning for Fabric auth helper functions.
- Minor config key normalization details where backward compatibility is preserved.

## Deferred Ideas

- Natural-language target resolution and explicit `onprem`/`fabric` switching commands (Phase 2).
- Fabric SQL endpoint query execution parity (Phase 3).
- Expanded dual-target guardrails and operator docs (Phase 4).

---

*Phase: 01-dual-target-foundation-and-auth*
*Discussion log generated: 2026-04-10*
