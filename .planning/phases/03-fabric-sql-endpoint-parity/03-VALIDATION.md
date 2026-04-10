---
phase: 3
slug: fabric-sql-endpoint-parity
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-10
---

# Phase 3 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Quick run command** | `.venv\Scripts\python -m pytest tests/test_target_routing.py -q` |
| **Full suite command** | `.venv\Scripts\python -m pytest -q` |
| **Estimated runtime** | ~30 seconds |

## Sampling Rate

- **After each task commit:** run targeted routing/fabric tests.
- **Before summary/verification:** run full suite.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 3-01-01 | 01 | 1 | FAB-02, FAB-03 | T-01 | Fabric workspace+endpoint+database resolve to configured SQL endpoint mapping only | unit | `.venv\Scripts\python -m pytest tests/test_settings_fabric.py -q` | ✅ | ✅ passed |
| 3-01-02 | 01 | 1 | FAB-04, FAB-05 | T-02 | Read-only query and metadata paths execute through target-aware connection resolver | unit | `.venv\Scripts\python -m pytest tests/test_target_routing.py -q -k "fabric or metadata or target_context"` | ✅ | ✅ passed |
| 3-01-03 | 01 | 1 | SAFE-04 | T-03 | SQL-only MCP surface preserved; docs/config explain Fabric SQL-only behavior | integration | `.venv\Scripts\python -m pytest -q` | ✅ | ✅ passed |

## Threat Mapping

| Threat | Description | Mitigation |
|--------|-------------|------------|
| T-01 | Fabric endpoint mapping bypass or accidental cross-workspace execution | Validate workspace/database/endpoint against allowlist and explicit mapping before connect |
| T-02 | Query context mismatch between routing and execution target | Build connection from the same active target object returned in `target_context` |
| T-03 | Scope creep to non-SQL Fabric operations | Keep MCP tool surface SQL-only; no new Fabric non-SQL tool handlers |

## Validation Sign-Off Checklist

- [x] All phase tasks have automated verification commands
- [x] Full suite passes
- [x] Requirement IDs FAB-02..05 and SAFE-04 mapped to tests/docs
- [x] `nyquist_compliant: true` remains set on completion
