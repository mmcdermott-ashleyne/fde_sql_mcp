from __future__ import annotations

import re
from threading import Lock
from typing import Any

from ..config import settings

_TARGET_LOCK = Lock()

_DATABASE_ENDPOINT_HINTS = {
    "core_dw": "warehouse",
    "core_lh": "lakehouse",
}

_WORKSPACE_ALIASES = {
    "dev": "fde_core_data_dev",
    "development": "fde_core_data_dev",
    "stg": "fde_core_data_stg",
    "stage": "fde_core_data_stg",
    "staging": "fde_core_data_stg",
    "prod": "fde_core_data_prod",
    "production": "fde_core_data_prod",
}

_SUPPORTED_ENDPOINT_TYPES = {"warehouse", "lakehouse"}


def _onprem_target_context() -> dict[str, Any]:
    return {
        "environment": "onprem",
        "workspace": None,
        "workspace_id": None,
        "endpoint_type": "sql_server",
        "database": settings.sql_database,
    }


_ACTIVE_TARGET: dict[str, Any] = _onprem_target_context()


def _extract_field(target: str, field: str) -> str | None:
    pattern = rf"{field}\s*[:=]\s*([A-Za-z0-9_\-]+)"
    match = re.search(pattern, target, flags=re.I)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def _workspace_id_by_workspace() -> dict[str, str]:
    normalized: dict[str, str] = {}
    allowed = {workspace.lower(): workspace for workspace in settings.fabric_allowed_workspaces}
    for workspace, workspace_id in settings.fabric_workspace_id_map.items():
        key = workspace.strip().lower()
        workspace_id_clean = workspace_id.strip()
        if not key or not workspace_id_clean:
            continue
        canonical = allowed.get(key, workspace.strip())
        normalized[canonical.lower()] = workspace_id_clean
    return normalized


def _workspace_by_id() -> dict[str, str]:
    lookup: dict[str, str] = {}
    for workspace_lower, workspace_id in _workspace_id_by_workspace().items():
        lookup[workspace_id.lower()] = workspace_lower
    return lookup


def _workspace_id_for(workspace: str) -> str | None:
    return _workspace_id_by_workspace().get(workspace.lower())


def _resolve_workspace_alias(token: str) -> str | None:
    alias = _WORKSPACE_ALIASES.get(token.lower())
    if alias:
        return alias
    return None


def _allowed_workspace_lookup() -> dict[str, str]:
    return {workspace.lower(): workspace for workspace in settings.fabric_allowed_workspaces}


def _default_workspace() -> str | None:
    allowed_lookup = _allowed_workspace_lookup()
    default_workspace = (settings.fabric_default_workspace or "").strip().lower()
    if not default_workspace:
        return None
    if default_workspace in allowed_lookup:
        return allowed_lookup[default_workspace]

    workspace_from_id = _workspace_by_id().get(default_workspace)
    if workspace_from_id and workspace_from_id in allowed_lookup:
        return allowed_lookup[workspace_from_id]
    return None


def _resolve_fabric_workspace(
    normalized_hint: str, explicit_workspace: str | None
) -> str:
    allowed_lookup = _allowed_workspace_lookup()
    workspace_by_id = _workspace_by_id()
    candidates: set[str] = set()

    if explicit_workspace:
        explicit = explicit_workspace.strip().lower()
        if explicit in allowed_lookup:
            candidates.add(allowed_lookup[explicit])
        if explicit in workspace_by_id:
            workspace_lower = workspace_by_id[explicit]
            if workspace_lower in allowed_lookup:
                candidates.add(allowed_lookup[workspace_lower])
        alias = _resolve_workspace_alias(explicit)
        if alias and alias.lower() in allowed_lookup:
            candidates.add(allowed_lookup[alias.lower()])
    else:
        for workspace_lower, canonical in allowed_lookup.items():
            if workspace_lower in normalized_hint:
                candidates.add(canonical)

        tokens = set(re.findall(r"[a-z0-9_]+", normalized_hint))
        for token in tokens:
            alias = _resolve_workspace_alias(token)
            if alias and alias.lower() in allowed_lookup:
                candidates.add(allowed_lookup[alias.lower()])

        for workspace_id, workspace_lower in workspace_by_id.items():
            if workspace_id in normalized_hint and workspace_lower in allowed_lookup:
                candidates.add(allowed_lookup[workspace_lower])

    if not candidates:
        default_workspace = _default_workspace()
        if default_workspace:
            candidates.add(default_workspace)

    if not candidates:
        raise ValueError(
            "Could not resolve a Fabric workspace from target hint. "
            "Use an allowlisted workspace name or mapped workspace ID."
        )

    if len(candidates) > 1:
        raise ValueError(
            "Target hint resolves to multiple Fabric workspaces; "
            "provide `workspace=<name or id>` for deterministic routing."
        )

    workspace = next(iter(candidates))
    if workspace.lower() not in allowed_lookup:
        raise ValueError(
            f"Resolved workspace `{workspace}` is not in the configured Fabric workspace allowlist."
        )
    return workspace


def _resolve_endpoint_type(
    normalized_hint: str,
    explicit_endpoint: str | None,
    explicit_database: str | None,
) -> str:
    if explicit_endpoint:
        endpoint = explicit_endpoint.strip().lower()
    elif "lakehouse" in normalized_hint or re.search(r"\blh\b", normalized_hint):
        endpoint = "lakehouse"
    elif "warehouse" in normalized_hint or re.search(r"\bdw\b", normalized_hint):
        endpoint = "warehouse"
    elif explicit_database:
        endpoint = _DATABASE_ENDPOINT_HINTS.get(
            explicit_database.strip().lower(), "warehouse"
        )
    else:
        endpoint = "warehouse"

    if endpoint not in _SUPPORTED_ENDPOINT_TYPES:
        raise ValueError(
            f"Unsupported Fabric endpoint type `{endpoint}`. "
            "Use `warehouse` or `lakehouse`."
        )
    return endpoint


def _resolve_database(
    normalized_hint: str, explicit_database: str | None, endpoint_type: str
) -> str:
    allowed_databases = tuple(db for db in settings.fabric_allowed_databases if db)
    if not allowed_databases:
        raise ValueError(
            "Fabric target routing requires configured `fabric_allowed_databases`."
        )

    allowed_lookup = {database.lower(): database for database in allowed_databases}

    if explicit_database:
        database = explicit_database.strip().lower()
        if database not in allowed_lookup:
            raise ValueError(
                f"Fabric database `{explicit_database}` is not in the configured allowlist."
            )
        resolved = allowed_lookup[database]
    else:
        candidates = {
            canonical
            for lower, canonical in allowed_lookup.items()
            if lower in normalized_hint
        }
        if len(candidates) > 1:
            raise ValueError(
                "Target hint resolves to multiple Fabric databases; "
                "provide `database=<name>` for deterministic routing."
            )
        if len(candidates) == 1:
            resolved = next(iter(candidates))
        else:
            preferred = "core_lh" if endpoint_type == "lakehouse" else "core_dw"
            if preferred in allowed_lookup:
                resolved = allowed_lookup[preferred]
            elif (
                settings.fabric_default_database
                and settings.fabric_default_database.lower() in allowed_lookup
            ):
                resolved = allowed_lookup[settings.fabric_default_database.lower()]
            elif len(allowed_databases) == 1:
                resolved = allowed_databases[0]
            else:
                raise ValueError(
                    "Could not resolve a Fabric database from target hint. "
                    "Use `database=<allowlisted_database>`."
                )

    expected_endpoint = _DATABASE_ENDPOINT_HINTS.get(resolved.lower())
    if expected_endpoint and endpoint_type != expected_endpoint:
        raise ValueError(
            f"Fabric endpoint `{endpoint_type}` is incompatible with database `{resolved}`."
        )
    return resolved


def resolve_query_target_impl(target: str) -> dict[str, Any]:
    hint = (target or "").strip()
    if not hint:
        raise ValueError("Target hint cannot be empty.")

    normalized_hint = hint.lower()
    if re.search(r"\bon[\s\-]?prem\b", normalized_hint):
        return _onprem_target_context()

    explicit_workspace = _extract_field(hint, "workspace")
    explicit_endpoint = _extract_field(hint, "endpoint")
    explicit_database = _extract_field(hint, "database")

    mentions_fabric = (
        "fabric" in normalized_hint
        or bool(explicit_workspace)
        or bool(explicit_endpoint)
        or bool(explicit_database)
        or any(alias in normalized_hint for alias in _WORKSPACE_ALIASES)
    )

    if not mentions_fabric:
        raise ValueError(
            "Target hint must resolve to `onprem` or `fabric` routing context."
        )

    workspace = _resolve_fabric_workspace(normalized_hint, explicit_workspace)
    endpoint_type = _resolve_endpoint_type(
        normalized_hint, explicit_endpoint, explicit_database
    )
    database = _resolve_database(normalized_hint, explicit_database, endpoint_type)

    return {
        "environment": "fabric",
        "workspace": workspace,
        "workspace_id": _workspace_id_for(workspace),
        "endpoint_type": endpoint_type,
        "database": database,
    }


def set_query_target_impl(target: str) -> dict[str, Any]:
    resolved = resolve_query_target_impl(target)
    with _TARGET_LOCK:
        _ACTIVE_TARGET.clear()
        _ACTIVE_TARGET.update(resolved)
        return dict(_ACTIVE_TARGET)


def get_query_target_impl() -> dict[str, Any]:
    with _TARGET_LOCK:
        return dict(_ACTIVE_TARGET)


def reset_query_target_impl() -> dict[str, Any]:
    with _TARGET_LOCK:
        _ACTIVE_TARGET.clear()
        _ACTIVE_TARGET.update(_onprem_target_context())
        return dict(_ACTIVE_TARGET)


def list_fabric_workspaces_impl() -> list[dict[str, Any]]:
    default_workspace = _default_workspace()
    workspace_ids = _workspace_id_by_workspace()
    items: list[dict[str, Any]] = []
    for workspace in sorted(settings.fabric_allowed_workspaces):
        items.append(
            {
                "workspace": workspace,
                "workspace_id": workspace_ids.get(workspace.lower()),
                "is_default": workspace == default_workspace,
            }
        )
    return items
