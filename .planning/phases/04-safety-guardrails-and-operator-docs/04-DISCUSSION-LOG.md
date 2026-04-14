# Phase 4: Safety Guardrails and Operator Docs - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves alternatives considered.

**Date:** 2026-04-13
**Phase:** 04-safety-guardrails-and-operator-docs
**Mode:** auto (`--auto --chain` equivalent)
**Areas discussed:** Cross-target read-only enforcement, guardrail consistency, operator documentation

---

## Cross-Target Read-Only Enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| Shared validator for both targets | Keep one validator path for `onprem` and `fabric` before execution | ✓ |
| Target-specific validators | Separate validation logic per target | |
| Relaxed Fabric validation | Keep strict on-prem and softer Fabric checks | |

**User's choice:** `[auto] Shared validator for both targets`
**Notes:** Selected to satisfy SAFE-01 with deterministic parity and no tool-surface expansion.

---

## Guardrail Consistency

| Option | Description | Selected |
|--------|-------------|----------|
| Uniform timeout/row/query caps | Apply same timeout, max query chars, and row cap logic to both targets | ✓ |
| Query-only parity | Keep parity for query path only; metadata path differs | |
| Fabric-specific limits | Apply different caps by target | |

**User's choice:** `[auto] Uniform timeout/row/query caps`
**Notes:** Selected to satisfy SAFE-02 and keep operator expectations consistent.

---

## Operator Documentation

| Option | Description | Selected |
|--------|-------------|----------|
| Expand existing README sections | Keep one docs surface with setup, auth precedence, and routing examples | ✓ |
| Separate operator runbook file | Add new dedicated markdown runbook | |
| Minimal doc delta | Keep docs terse and rely on implicit behavior | |

**User's choice:** `[auto] Expand existing README sections`
**Notes:** Selected to satisfy CONF-03 while minimizing doc sprawl.

---

## the agent's Discretion

- Exact test organization for read-only validator and cross-target guardrail checks.
- Final README heading structure and example formatting.

## Deferred Ideas

- Dedicated diagnostics endpoint and structured audit output (`OPS-01`, `OPS-02`) deferred to future milestone work.

