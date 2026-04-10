---
phase: 1
slug: dual-target-foundation-and-auth
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-10
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | none |
| **Quick run command** | `.venv\\Scripts\\python -m pytest tests/test_settings_fabric.py -q` |
| **Full suite command** | `.venv\\Scripts\\python -m pytest -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `.venv\\Scripts\\python -m pytest tests/test_settings_fabric.py -q`
- **After every plan wave:** Run `.venv\\Scripts\\python -m pytest -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | CONF-01, ROUTE-01 | T-01 / config-safety | Existing SQL defaults remain intact while Fabric settings are additive | unit | `.venv\\Scripts\\python -m pytest tests/test_settings_fabric.py -q -k "existing_sql_defaults"` | ✅ | ⬜ pending |
| 1-01-02 | 01 | 1 | AUTH-01, AUTH-02, AUTH-03 | T-02 / auth-mode | Fabric mode selection is deterministic and single-tenant | unit | `.venv\\Scripts\\python -m pytest tests/test_settings_fabric.py -q -k "fabric_auth"` | ✅ | ⬜ pending |
| 1-01-03 | 01 | 1 | AUTH-01, AUTH-02 | T-03 / diagnostics | Auth diagnostics expose non-secret mode and source details only | unit | `.venv\\Scripts\\python -m pytest tests/test_settings_fabric.py -q -k "auth_diagnostics"` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have automated verify steps
- [x] Sampling continuity maintained
- [x] No watch-mode flags
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
