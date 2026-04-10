# Testing Patterns

**Analysis Date:** 2026-04-10

## Test Framework

**Runner:**
- `pytest` is declared in optional dev dependencies (`pyproject.toml`).
- Config: Not detected (`jest.config.*`, `vitest.config.*`, `pytest.ini`, and `[tool.pytest.ini_options]` are absent).

**Assertion Library:**
- `pytest` native `assert` style is the implied default (no alternative assertion library configured in `pyproject.toml`).

**Run Commands:**
```bash
py -m pytest                 # Run all tests (current result: no tests collected)
py -m pytest -q              # Quiet mode (current result: no tests collected)
py -m pytest --maxfail=1     # Early-fail run for future suites
```

## Test File Organization

**Location:**
- No test files detected. Repository contains no files matching `*.test.*` or `*.spec.*`.

**Naming:**
- Not established. Define Python tests as `test_*.py` under a top-level `tests/` directory to match pytest defaults.

**Structure:**
```text
Not detected in current repository state.
```

## Test Structure

**Suite Organization:**
```python
Not detected (no test modules found).
```

**Patterns:**
- Setup pattern: Not detected.
- Teardown pattern: Not detected.
- Assertion pattern: Not detected.

## Mocking

**Framework:** Not detected.

**Patterns:**
```python
Not detected (no uses of unittest.mock, pytest-mock, or monkeypatch in repository files).
```

**What to Mock:**
- Mock `pyodbc` connection/cursor behavior when testing `src/fde_sql_mcp/clients/sql.py` and `src/fde_sql_mcp/tools/databases.py`.
- Mock environment/config inputs for `src/fde_sql_mcp/config.py` (`os.getenv`, local config loader behavior).

**What NOT to Mock:**
- Do not mock pure validation logic in `src/fde_sql_mcp/tools/databases.py` (`_strip_sql_comments_and_literals`, `_validate_readonly_query`, `_normalize_max_rows`).
- Do not mock simple adapter routing in `src/fde_sql_mcp/server.py`; call handlers and assert delegation/output shape.

## Fixtures and Factories

**Test Data:**
```python
Not detected (no fixtures/factories present).
```

**Location:**
- Not detected (`conftest.py` absent).

## Coverage

**Requirements:** None enforced (no coverage config or threshold in `pyproject.toml` and no CI config detected in repository files).

**View Coverage:**
```bash
Not configured in-repo. Add pytest-cov to dev dependencies before using coverage commands.
```

## Test Types

**Unit Tests:**
- Not present. Highest-priority unit targets are query validation and normalization logic in `src/fde_sql_mcp/tools/databases.py` and config parsing in `src/fde_sql_mcp/config.py`.

**Integration Tests:**
- Not present. Integration tests against a SQL Server test instance are not defined for `src/fde_sql_mcp/clients/sql.py`.

**E2E Tests:**
- Not used. No MCP end-to-end test harness is checked in for `src/fde_sql_mcp/server.py`.

## Common Patterns

**Async Testing:**
```python
Not detected. Async MCP tool functions exist in `src/fde_sql_mcp/server.py` and would require pytest async support for direct coroutine testing.
```

**Error Testing:**
```python
Not detected. Error paths currently untested (RuntimeError/ValueError branches in `src/fde_sql_mcp/config.py`, `src/fde_sql_mcp/clients/sql.py`, and `src/fde_sql_mcp/tools/databases.py`).
```

---

*Testing analysis: 2026-04-10*
