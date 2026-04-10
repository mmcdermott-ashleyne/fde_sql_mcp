# Phase 2: Target Routing and Governance - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `02-CONTEXT.md`.

**Date:** 2026-04-10
**Phase:** 2-target-routing-and-governance
**Mode:** Auto chain equivalent (`--auto --chain`)
**Areas discussed:** target selection UX, Fabric allowlist governance, response context

---

## Target Selection UX

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit target command only | Require structured fields for every switch | |
| Explicit + natural-language hint parsing | Accept freeform target hints and resolve deterministically | ✓ |
| Natural-language only | Infer all routing from free text without explicit tools | |

**User's choice:** Explicit + natural-language hint parsing (auto-selected)
**Notes:** Preserve existing SQL tool signatures; routing is additive.

---

## Fabric Governance and Allowlists

| Option | Description | Selected |
|--------|-------------|----------|
| Name allowlist only | Restrict by workspace names only | |
| Name allowlist + workspace ID mapping | Restrict by approved names and mapped IDs | ✓ |
| Open Fabric selection | Allow any accessible workspace/database | |

**User's choice:** Name allowlist + workspace ID mapping (auto-selected)
**Notes:** Reject out-of-allowlist workspace/database requests and ambiguous resolution.

---

## Response Context

| Option | Description | Selected |
|--------|-------------|----------|
| Keep query response unchanged | No target context returned | |
| Add resolved target context in query responses | Include environment/workspace/endpoint/database details | ✓ |
| Return context only through separate diagnostics tool | Query payload unchanged; separate lookup required | |

**User's choice:** Add resolved target context in query responses (auto-selected)
**Notes:** Supports ROUTE-04 without renaming existing query tools.

---

## the agent's Discretion

- Parser tokenization and ambiguity-handling details for natural-language routing.
- Internal state container shape for active target tracking.

## Deferred Ideas

- Fabric SQL execution path implementation remains deferred to Phase 3.
- Cross-target safety parity and expanded operator docs remain deferred to Phase 4.
