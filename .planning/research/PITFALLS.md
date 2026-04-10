# Pitfalls Research

**Domain:** Dual-target SQL MCP (on-prem SQL Server + Fabric SQL endpoints)
**Researched:** 2026-04-10
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Non-deterministic auth fallback selects the wrong identity

**What goes wrong:**
Client-secret/browser fallback silently authenticates as an unintended principal (CLI user, cached token user, or home-tenant user), causing cross-environment data exposure or hard-to-debug permission failures.

**Why it happens:**
`DefaultAzureCredential` chains many credentials by default, continues through developer credentials, and excludes interactive browser auth unless explicitly enabled.

**How to avoid:**
- Implement explicit auth mode routing, not implicit chain fallback:
  - `service_principal` when `FABRIC_TENANT_ID` + `FABRIC_CLIENT_ID` + `FABRIC_CLIENT_SECRET` are all present and valid.
  - `interactive_browser` only when explicitly enabled for local/dev.
- Set tenant explicitly for interactive flows (single-tenant enforcement).
- Fail closed on ambiguous auth state (partial env vars or multiple valid credentials).
- Log selected credential type and tenant ID on connect (no secrets).

**Warning signs:**
- Same machine/user alternates between successful and denied access without code changes.
- Queries unexpectedly hit prod while testing dev.
- Auth errors vary by machine/session (`CredentialUnavailableError`/`ClientAuthenticationError` patterns differ).

**Phase to address:**
Phase A: Auth foundation and credential precedence

---

### Pitfall 2: SPN is configured in code but blocked by Fabric tenant/workspace controls

**What goes wrong:**
Service principal auth appears correct but SQL endpoint connections fail because Fabric tenant developer settings/security groups/workspace permissions are incomplete.

**Why it happens:**
Fabric requires admin-side enablement and security-group allowlisting for service principals, plus workspace/item access and correct SQL endpoint permissions.

**How to avoid:**
- Add a startup/health preflight for Fabric target:
  - Tenant developer setting enabled for SPN API usage.
  - SPN is in allowed security group.
  - SPN has workspace/item-level access for target workspace.
  - Target database/catalog exists and is allowed.
- Add runbook checks for permission model layering (Entra auth -> Fabric access -> data security).

**Warning signs:**
- Login succeeds in Entra but SQL connection fails with authorization/permission errors.
- Error: token principal authenticated but database not found/insufficient permission.
- Works for user identity but not for SPN.

**Phase to address:**
Phase A: Auth foundation and credential precedence

---

### Pitfall 3: ODBC auth mode mixing causes broken or insecure connections

**What goes wrong:**
Connections fail or downgrade unexpectedly when auth attributes are mixed incorrectly (token + `UID/PWD`/`Trusted_Connection`/`Authentication`) or encryption behavior is assumed instead of explicitly set.

**Why it happens:**
ODBC Entra auth rules are strict: access token mode is mutually exclusive with other auth keywords, and encryption defaults vary by driver/auth mode.

**How to avoid:**
- Use one auth pattern per connection attempt:
  - SPN: `Authentication=ActiveDirectoryServicePrincipal` + `UID`/`PWD`.
  - Access-token mode: set `SQL_COPT_SS_ACCESS_TOKEN` only; omit conflicting auth fields.
- Explicitly set `Encrypt=yes` and `TrustServerCertificate=no` for Fabric/cloud connections.
- Pin/test ODBC driver versions that support required auth modes.

**Warning signs:**
- Intermittent login failures across driver versions/hosts.
- Connection succeeds on one OS and fails on another with same credentials.
- TLS or certificate warnings appear only in some environments.

**Phase to address:**
Phase A: Auth foundation and credential precedence

---

### Pitfall 4: Allowlisting by mutable names enables routing drift or bypass

**What goes wrong:**
Target selection drifts from intended environment boundaries (dev/stg/prod) because routing trusts mutable workspace/database names or unvalidated user input.

**Why it happens:**
Dual-target systems often start with string matching, then add natural-language selection and dynamic database inputs. Names are mutable; IDs are stable.

**How to avoid:**
- Enforce allowlists on immutable identifiers:
  - Fabric: workspace IDs + explicit endpoint host patterns + allowed catalogs.
  - On-prem: server/database allowlist and strict database-name regex.
- Resolve natural-language target selection to a canonical target ID before connect.
- Reject unknown/ambiguous targets; no silent fallback.
- Separate allowlist config for Fabric and on-prem with explicit environment labels.

**Warning signs:**
- Same prompt resolves to different targets over time.
- Unexpected database appears in successful query results.
- Security review finds name-based matching logic in routing path.

**Phase to address:**
Phase B: Target routing and allowlist enforcement

---

### Pitfall 5: Shared query wrapper is SQL Server-specific and breaks on Fabric T-SQL surface

**What goes wrong:**
Read-only execution works on on-prem SQL Server but fails on Fabric because shared wrapper injects unsupported statements or relies on SQL Server-only metadata behavior.

**Why it happens:**
Current shared execution path prepends `SET ROWCOUNT`; Fabric Warehouse docs explicitly list `SET ROWCOUNT` as unsupported. Reusing the same metadata/query wrapper across engines without capability checks causes runtime failures.

**How to avoid:**
- Split execution policy by dialect/target profile:
  - SQL Server profile: keep `SET ROWCOUNT`.
  - Fabric profile: enforce row limits by wrapping user query (`SELECT TOP`) or paged fetch pattern, not `SET ROWCOUNT`.
- Add capability matrix tests per target for: row limiting, metadata listing, timeout behavior, and comment/CTE handling.
- Keep one tool surface, but route through target-specific execution adapters.

**Warning signs:**
- Fabric queries fail immediately with syntax/unsupported command errors.
- Metadata tools pass on on-prem but fail on Fabric endpoints.
- New “shared” fixes repeatedly regress one target.

**Phase to address:**
Phase C: Dual-target query engine abstraction

---

### Pitfall 6: Security model mismatch leads to accidental overexposure in SQL analytics endpoint

**What goes wrong:**
Users/SPNs get broader data access than expected because SQL endpoint mode/roles don’t match security assumptions (for example, workspace elevated roles bypass OneLake restrictions).

**Why it happens:**
Fabric SQL analytics endpoints can run with different access modes and role semantics; Admin/Member/Contributor can bypass OneLake enforcement in user identity mode.

**How to avoid:**
- Document and enforce allowed security mode per environment.
- For restricted reader scenarios, require Viewer/read-only patterns and validate role assignments.
- Add authorization tests for least-privilege expectations (same query under Viewer vs Contributor).
- Include security-mode and role checks in deployment/preflight scripts.

**Warning signs:**
- RLS/CLS appears configured but users still see full tables.
- Access differs sharply between Viewer and Contributor without code changes.
- Security sync/role propagation errors in SQL analytics endpoint.

**Phase to address:**
Phase D: Authorization and security hardening

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Using one generic connection-string builder for both targets | Faster initial implementation | Auth and encryption bugs per target; hard-to-debug failures | Only for throwaway spike code |
| Name-based allowlisting only | Quick config and readability | Environment drift and bypass risk after renames | Never for production routing |
| Reusing SQL Server query preamble on Fabric (`SET ROWCOUNT`) | Minimal refactor | Systematic runtime failures on Fabric | Never |
| Silent fallback from SPN to interactive/browser | Fewer immediate auth failures | Identity drift, non-reproducible behavior, hidden privilege changes | Dev-only with explicit opt-in flag and visible logs |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Fabric tenant settings | Assuming app registration alone enables SPN connectivity | Verify tenant developer setting + allowed security group + workspace/item permissions before rollout |
| ODBC Entra auth | Mixing access token mode with `UID/PWD` or `Trusted_Connection` | Use mutually exclusive auth modes and explicit encryption settings |
| Fabric network/firewall | Opening only portal endpoints and missing SQL/TDS/service tags | Allow required Fabric SQL endpoints and TCP 1433 (plus documented redirect/related ports where applicable) |
| SQL analytics endpoint security | Assuming workspace role == OneLake table restrictions | Validate access mode and role behavior; test Viewer vs elevated roles |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Full `fetchall()` on shared query path | Memory spikes and slow MCP responses on large result sets | Use `fetchmany()`/pagination and hard caps per tool | Typically visible when result sets exceed tens of thousands of rows |
| No retry strategy for Fabric transient errors | Sporadic query failures during platform updates | Add bounded retry with idempotent read semantics and jitter | Becomes frequent under concurrent workloads and service updates |
| No target-specific metadata caching | Repeated schema calls amplify latency | Cache stable metadata with short TTL per target | Noticeable when many clients call list APIs repeatedly |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Allowing runtime disable of read-only enforcement in dual-target mode | Write operations can slip into production endpoints | Keep read-only enforcement immutable in production profile |
| Accepting raw database names into connection strings | Connection-string injection and target escape | Validate against strict pattern and allowlist before constructing connection string |
| `TrustServerCertificate=yes` defaults in cloud paths | MITM and weakened TLS trust model | Default to `TrustServerCertificate=no` for Fabric/cloud and require explicit override |
| Broad SPN workspace roles for convenience | Excessive data access blast radius | Grant least-privilege item access and validate effective permissions |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Ambiguous environment selection language | Users query wrong environment unintentionally | Echo resolved target (env/workspace/database) before execution |
| Generic auth error messages | Users cannot self-correct misconfiguration | Map known auth failures to actionable diagnostics (tenant setting, permission, catalog) |
| Hiding effective auth mode | Hard to trust and audit behavior | Return non-secret execution metadata: auth mode, target type, resolved environment |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **SPN auth path:** Tenant developer setting and security-group allowlisting validated in target tenant.
- [ ] **Browser fallback path:** Explicitly disabled by default in non-dev environments.
- [ ] **Target routing:** Natural-language selection resolves to canonical allowlisted IDs, not names.
- [ ] **Fabric query execution:** No unsupported `SET ROWCOUNT` or SQL Server-only preamble in Fabric profile.
- [ ] **Read-only guarantees:** Enforcement cannot be disabled in production runtime.
- [ ] **Permission model tests:** Viewer/read-only and elevated-role behavior validated on SQL analytics endpoint.

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong identity selected by fallback | MEDIUM | Disable fallback path, force explicit auth mode, rotate/revoke cached credentials, re-run least-privilege tests |
| SPN blocked by tenant/workspace settings | LOW | Validate tenant developer setting, security-group membership, workspace/item permissions, then retest with known query |
| Fabric break from shared SQL wrapper | MEDIUM | Hotfix Fabric adapter to remove unsupported statements, deploy target-specific row-limit strategy, add regression tests |
| Allowlist drift/bypass | HIGH | Freeze routing to ID-based allowlist, audit access logs for off-allowlist execution, rotate credentials if exposure suspected |
| Overexposed access via role/mode mismatch | HIGH | Downgrade workspace roles, enforce approved access mode, run permission diff and incident review |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Non-deterministic auth fallback | Phase A: Auth foundation and credential precedence | Integration tests proving deterministic credential selection across env-var combinations |
| SPN blocked by tenant/workspace controls | Phase A: Auth foundation and credential precedence | Preflight check returns green for tenant setting, group allowlist, and workspace/item access |
| ODBC auth mode mixing | Phase A: Auth foundation and credential precedence | Connection-matrix tests by auth mode and driver version pass |
| Mutable-name allowlist drift | Phase B: Target routing and allowlist enforcement | Routing tests confirm only canonical allowlisted IDs are executable |
| SQL Server-specific wrapper on Fabric | Phase C: Dual-target query engine abstraction | Same query test suite passes on on-prem and Fabric profiles |
| Permission model mismatch in SQL analytics endpoint | Phase D: Authorization and security hardening | Role-based access tests validate least privilege for Viewer/read-only scenarios |
| Missing retries/observability for transient failures | Phase E: Reliability and observability | Error budget and retry metrics show controlled transient-failure recovery |

## Sources

- Microsoft Fabric Warehouse connectivity (auth types, initial catalog requirement, limitations): https://learn.microsoft.com/en-us/fabric/data-warehouse/connectivity
- Microsoft Fabric Entra authentication for Warehouse/SQL analytics endpoint (tenant/workspace prerequisites, SPN support): https://learn.microsoft.com/en-us/fabric/data-warehouse/entra-id-authentication
- Microsoft Fabric developer tenant settings (SPN security-group requirement): https://learn.microsoft.com/en-us/fabric/admin/service-admin-portal-developer
- Microsoft Fabric T-SQL surface area (`SET ROWCOUNT` unsupported): https://learn.microsoft.com/en-us/fabric/data-warehouse/tsql-surface-area
- OneLake security for SQL analytics endpoint (role bypass and mode behavior): https://learn.microsoft.com/en-us/fabric/onelake/security/sql-analytics-endpoint-onelake-security
- Fabric URL/port allowlist requirements: https://learn.microsoft.com/en-us/fabric/security/fabric-allow-list-urls
- ODBC Entra authentication rules and attribute constraints: https://learn.microsoft.com/en-us/sql/connect/odbc/using-azure-active-directory?view=sql-server-ver17
- ODBC connection keyword reference (auth modes): https://learn.microsoft.com/en-us/sql/connect/odbc/dsn-connection-string-attribute?view=sql-server-ver17
- Azure Identity for Python (`DefaultAzureCredential` continuation behavior and defaults): https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python
- Azure Identity `DefaultAzureCredential` API (interactive default exclusion and tenant behavior): https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python
- Azure Identity `InteractiveBrowserCredential` API (production caveats and interactive requirements): https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.interactivebrowsercredential?view=azure-python
- Repository context for shared execution and connection behavior:
  - `.planning/PROJECT.md`
  - `.planning/codebase/CONCERNS.md`
  - `src/fde_sql_mcp/tools/databases.py`
  - `src/fde_sql_mcp/clients/sql.py`

---
*Pitfalls research for: dual-target SQL MCP auth/routing and shared read-only execution*
*Researched: 2026-04-10*
