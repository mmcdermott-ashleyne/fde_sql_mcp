---
phase: 4
slug: safety-guardrails-and-operator-docs
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-13
---

# Phase 4 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Quick run command** | `.venv\Scripts\python -m pytest tests/test_query_guardrails.py -q` |
| **Full suite command** | `.venv\Scripts\python -m pytest -q` |
| **Estimated runtime** | ~35 seconds |

## Sampling Rate

- **After each task commit:** run task-scoped tests.
- **Before summary/verification:** run full suite.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 4-01-01 | 01 | 1 | SAFE-01, SAFE-02 | T-01, T-02 | Read-only validation, query length cap, timeout assignment, and row cap behavior stay consistent for on-prem and Fabric targets | unit | `.venv\Scripts\python -m pytest tests/test_query_guardrails.py -q` | ✅ | pending |
| 4-01-02 | 01 | 1 | SAFE-02 | T-02 | Shared guardrail helper logic is used by both query and metadata execution paths | unit | `.venv\Scripts\python -m pytest tests/test_query_guardrails.py -q -k "timeout or metadata"` | ✅ | pending |
| 4-01-03 | 01 | 1 | CONF-03 | T-03 | Operator docs explain dual-environment setup/auth precedence and explicit/natural routing examples | integration | `.venv\Scripts\python -m pytest -q` | ✅ | pending |

## Threat Mapping

| Threat | Description | Mitigation |
|--------|-------------|------------|
| T-01 | Read-only validator applies differently by target | Add cross-target tests using shared query validation entrypoint |
| T-02 | Timeout/row-limit handling drifts between query and metadata paths | Introduce shared timeout helper and verify invocation in tests |
| T-03 | Operators misconfigure dual-target routing due to incomplete docs | Expand README with configuration checklist and routing examples |

## Validation Sign-Off Checklist

- [x] All phase tasks have automated verification commands
- [ ] Full suite passes
- [x] Requirement IDs SAFE-01, SAFE-02, CONF-03 mapped to tests/docs
- [ ] `nyquist_compliant: true` remains set on completion
