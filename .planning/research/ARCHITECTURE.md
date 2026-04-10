# Architecture Research

**Domain:** Dual-target SQL MCP server (on-prem SQL Server + Fabric SQL endpoints)
**Researched:** 2026-04-10
**Confidence:** HIGH

## Standard Architecture

### System Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                         MCP Transport Layer                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│  FastMCP Tool Wrappers (existing names/signatures stay stable)             │
│  ping, list_tables, run_readonly_query, ...                                │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────────┐
│                      Routing + Context Layer                                │
├──────────────────────────────────────────────────────────────────────────────┤
│ RouteResolver: chooses target (onprem | fabric) per request/client         │
│ TargetContextStore: per-client selected target/environment                  │
│ TargetPolicy: allowlists for workspaces/databases                           │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────────┐
│                Shared Read-Only SQL Service Layer                           │
├──────────────────────────────────────────────────────────────────────────────┤
│ QueryGuard (single validator) + MetadataQueryService (shared SQL surface)  │
│ No target-specific MCP tools                                                │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────────┐
│                Connector + Endpoint Adapter Layer                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ OnPremConnector (Trusted_Connection)   FabricConnector (AAD token ODBC)    │
│ StaticEndpointProvider                  FabricEndpointResolver (REST lookup)│
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────────────┐
│                        Data/Platform Layer                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ On-prem SQL Server         Fabric Warehouse/Lakehouse SQL endpoint          │
│ Local/AD auth              Azure credential + Fabric/API allowlists         │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| MCP tool wrappers (`server.py`) | Keep current tool contract stable; delegate only | Thin async `@mcp.tool` functions using `asyncio.to_thread` |
| Route resolver | Decide target and endpoint for each request | Pure function/class with precedence rules and policy checks |
| Target context store | Persist selected environment per MCP client | In-memory dict keyed by `ctx.client_id` (same pattern as `fde_fabric_mcp`) |
| Shared SQL service | Run metadata + read-only query flow once for all targets | Reuse `tools/databases.py` logic with connector abstraction |
| Connector factory | Return concrete connector for selected target | Strategy/factory returning on-prem or Fabric connector |
| Fabric endpoint resolver | Resolve workspace/item to SQL server+database | REST client adapted from `fde_fabric_mcp/core/sql_endpoints.py` |
| Query guardrails | Enforce read-only and row/query limits uniformly | Existing validator in `tools/databases.py` made target-agnostic |

## Recommended Project Structure

```text
src/fde_sql_mcp/
├── server.py                     # Existing MCP tool surface (minimal changes)
├── config.py                     # Existing settings + target/auth/allowlist config
├── core/
│   ├── routing.py                # RouteResolver + precedence rules
│   ├── context_store.py          # Per-client selected target/environment
│   └── policies.py               # Workspace/database allowlist checks
├── clients/
│   ├── sql_onprem.py             # Current pyodbc Trusted_Connection path
│   ├── sql_fabric.py             # pyodbc token-based Fabric SQL path
│   └── fabric_endpoints.py       # Fabric REST SQL endpoint resolution
├── services/
│   └── readonly_sql.py           # Shared metadata/read-only execution logic
└── tools/
    └── databases.py              # Existing impl entrypoints; delegates to services
```

### Structure Rationale

- **`core/`:** Keeps routing, context, and policy decisions out of tool wrappers and SQL execution code.
- **`clients/`:** Makes transport/auth differences explicit while preserving one shared query path.
- **`services/readonly_sql.py`:** Centralizes validation and SQL execution semantics so both targets behave identically.
- **`tools/databases.py`:** Remains the stable MCP-facing module, minimizing surface churn and prompt-token impact.

## Architectural Patterns

### Pattern 1: Target Routing Strategy

**What:** Resolve request target once, then execute through the matching connector.
**When to use:** Any tool that runs SQL or metadata queries.
**Trade-offs:** Adds one indirection layer, but prevents branching logic duplication in every tool.

**Example:**
```python
route = route_resolver.resolve(ctx=ctx, database=database, target_hint=target)
connector = connector_factory.for_target(route.target_type, route.endpoint)
return readonly_sql_service.run_query(connector, query, max_rows=max_rows)
```

### Pattern 2: Client-Scoped Environment Context

**What:** Store selected environment/target per MCP client and apply by default.
**When to use:** Sessions where user runs multiple related tools against same environment.
**Trade-offs:** Requires explicit reset/diagnostic tools; in-memory context is process-local.

**Example:**
```python
context_store.set(ctx, "sql_target", {"type": "fabric", "workspace": "fde_core_data_dev"})
target = context_store.get(ctx, "sql_target") or settings.default_sql_target
```

### Pattern 3: Shared Guardrails Before Connector Execution

**What:** Validate SQL and limits before any target-specific execution.
**When to use:** Every query path (`run_readonly_query`, metadata introspection where applicable).
**Trade-offs:** Slightly stricter behavior across targets, but guarantees consistent safety.

## Data Flow

### Request Flow

```text
MCP Client Tool Call
    ↓
server.py tool wrapper (same signature as today)
    ↓
RouteResolver (explicit arg > client context > config default)
    ↓
TargetPolicy checks (workspace/database allowlist)
    ↓
Shared QueryGuard (readonly, limits)
    ↓
ConnectorFactory
    ↓
OnPremConnector OR FabricConnector
    ↓
SQL execution + row dict mapping
    ↓
JSON response through FastMCP
```

### State Management

```text
settings (process-wide immutable config)
    +
TargetContextStore (per client_id, in-memory)
    +
Optional endpoint cache (Fabric endpoint resolution TTL)
```

### Key Data Flows

1. **On-prem flow:** Tool call -> route=`onprem` -> static SQL Server endpoint from config -> Trusted_Connection pyodbc -> response.
2. **Fabric flow:** Tool call -> route=`fabric` -> resolve workspace/item SQL endpoint (allowlisted) -> acquire AAD token -> pyodbc token auth -> response.
3. **Contexted flow:** User selects environment once -> subsequent tools omit target details -> resolver applies stored context.

## Build Order Implications

1. **Stabilize shared service boundary first.**
   - Extract current query/metadata behavior into a target-agnostic service without changing tool signatures.
   - This de-risks all later work by preserving existing on-prem behavior.
2. **Add routing/context layer second.**
   - Introduce resolver + client context store while still routing only to on-prem.
   - Enables environment-aware behavior without Fabric dependency yet.
3. **Add Fabric connector third.**
   - Implement token-based connector and endpoint resolver; plug into factory.
   - Tool surface remains unchanged, limiting regression scope.
4. **Add allowlist policy enforcement before broad testing.**
   - Enforce workspace/database restrictions centrally before enabling Fabric by default.
5. **Only then add optional UX helpers.**
   - Optional `set_target`/`get_target` tools or lightweight target hints can be layered last with no impact on core SQL tools.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k requests/day | In-memory context store + no pool is fine; keep process simple |
| 1k-100k requests/day | Add endpoint resolution cache + structured logging + per-target timeout tuning |
| 100k+ requests/day | Add connection pooling strategy, distributed context/cache, and horizontal MCP workers |

### Scaling Priorities

1. **First bottleneck:** Fabric endpoint resolution and token acquisition latency. Fix with short TTL caches and credential reuse.
2. **Second bottleneck:** ODBC connection churn per request. Fix with controlled pooling and worker-level concurrency limits.

## Anti-Patterns

### Anti-Pattern 1: Duplicating Tool Surface by Target

**What people do:** Create parallel tools like `fabric_list_tables` and `onprem_list_tables`.
**Why it's wrong:** Doubles maintenance and increases prompt/context overhead.
**Do this instead:** Keep one tool surface and route internally by target context.

### Anti-Pattern 2: Embedding Routing Logic in Every Tool Function

**What people do:** Add per-tool `if target == ...` blocks in `server.py`.
**Why it's wrong:** Scatters policy logic and creates inconsistent behavior.
**Do this instead:** Route once in a shared resolver/service path.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| On-prem SQL Server | pyodbc with `Trusted_Connection=yes` | Existing implementation in `src/fde_sql_mcp/clients/sql.py` |
| Fabric SQL endpoint | pyodbc with AAD access token (`attrs_before` token) | Reuse pattern from `fde_fabric_mcp/src/fde_fabric_mcp/clients/sql.py` |
| Fabric REST API | Resolve workspace/item -> SQL endpoint host | Reuse endpoint lookup pattern from `fde_fabric_mcp/src/fde_fabric_mcp/core/sql_endpoints.py` |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `server.py` ↔ routing/service layer | Direct function calls | Keep `server.py` thin and stable |
| routing ↔ policies | Direct function calls | Central point for allowlist enforcement |
| service ↔ connector factory | Interface/protocol | Enables shared query code for both targets |
| connectors ↔ config/auth | Settings + credential providers | Keeps auth concerns out of query logic |

## Sources

- `.planning/PROJECT.md` (project requirements and constraints, read 2026-04-10)
- `src/fde_sql_mcp/server.py` (current tool-surface and delegation shape, read 2026-04-10)
- `src/fde_sql_mcp/clients/sql.py` (current on-prem connector implementation, read 2026-04-10)
- `src/fde_sql_mcp/tools/databases.py` (shared read-only validation and SQL execution behavior, read 2026-04-10)
- `src/fde_sql_mcp/config.py` (current config loading and guardrail settings, read 2026-04-10)
- `C:/Users/mmcdermott/OneDrive - Factory Direct of Edison/dev/repositories/fde_fabric_mcp/src/fde_fabric_mcp/auth.py` (Fabric auth pattern, read 2026-04-10)
- `C:/Users/mmcdermott/OneDrive - Factory Direct of Edison/dev/repositories/fde_fabric_mcp/src/fde_fabric_mcp/clients/sql.py` (Fabric SQL token ODBC pattern, read 2026-04-10)
- `C:/Users/mmcdermott/OneDrive - Factory Direct of Edison/dev/repositories/fde_fabric_mcp/src/fde_fabric_mcp/core/context_store.py` (per-client context pattern, read 2026-04-10)
- `C:/Users/mmcdermott/OneDrive - Factory Direct of Edison/dev/repositories/fde_fabric_mcp/src/fde_fabric_mcp/core/sql_endpoints.py` (endpoint resolution pattern, read 2026-04-10)
- `C:/Users/mmcdermott/OneDrive - Factory Direct of Edison/dev/repositories/fde_fabric_mcp/src/fde_fabric_mcp/core/guardrails.py` (allowlist/read-only guardrail pattern, read 2026-04-10)

---
*Architecture research for: dual-target SQL MCP*
*Researched: 2026-04-10*
