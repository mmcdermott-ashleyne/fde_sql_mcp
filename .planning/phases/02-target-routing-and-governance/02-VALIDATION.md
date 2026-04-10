---
phase: 2
slug: target-routing-and-governance
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-10
---

# Phase 2 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none |
| **Quick run command** | `.venv\Scripts\python -m pytest tests/test_target_routing.py -q` |
| **Full suite command** | `.venv\Scripts\python -m pytest -q` |
| **Estimated runtime** | ~20 seconds |

## Sampling Rate

- **After every task commit:** Run `.venv\Scripts\python -m pytest tests/test_target_routing.py -q`
- **After wave completion:** Run `.venv\Scripts\python -m pytest -q`
- **Before verification:** Full suite must pass

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 01 | 1 | ROUTE-02, ROUTE-03, FAB-01, SAFE-03 | T-02 | Router rejects out-of-allowlist targets and ambiguous hints | unit | `.venv\Scripts\python -m pytest tests/test_target_routing.py -q -k "resolve or allowlist"` | ✅ | ⬜ pending |
| 2-01-02 | 01 | 1 | ROUTE-04, CONF-02 | T-03 | Query response includes target context bound to resolved target | unit | `.venv\Scripts\python -m pytest tests/test_target_routing.py -q -k "target_context"` | ✅ | ⬜ pending |
| 2-01-03 | 01 | 1 | ROUTE-02, ROUTE-03, FAB-01, CONF-02 | T-01, T-04 | Tool surface remains additive and existing SQL tests remain green | integration | `.venv\Scripts\python -m pytest -q` | ✅ | ⬜ pending |

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

## Manual-Only Verifications

None — all phase behaviors have automated verification.

## Validation Sign-Off

- [ ] All tasks have automated verification
- [ ] No watch-mode commands
- [ ] Feedback latency stays under 30 seconds
- [ ] `nyquist_compliant: true` set at completion

**Approval:** pending
