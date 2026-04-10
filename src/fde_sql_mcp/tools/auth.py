from __future__ import annotations

from typing import Any, Dict

from ..config import settings


def _credential_source_for_mode(mode: str) -> str:
    if mode == "client_secret":
        return "fabric_client_secret"
    if mode == "browser":
        return "browser_capable_default"
    if mode == "default_browser":
        return "browser_capable_default"
    return mode


def get_auth_info_impl() -> Dict[str, Any]:
    """
    Return non-secret authentication diagnostics for this MCP server.
    """

    mode = settings.fabric_auth_mode
    return {
        "fabric_enabled": settings.fabric_enabled,
        "auth_mode": mode,
        "tenant_context": settings.fabric_tenant_context,
        "credential_source": _credential_source_for_mode(mode),
        "configured_inputs": {
            "fabric_tenant_id": bool(settings.fabric_tenant_id),
            "fabric_client_id": bool(settings.fabric_client_id),
            "fabric_client_secret": bool(settings.fabric_client_secret),
            "fabric_default_workspace": bool(settings.fabric_default_workspace),
            "fabric_default_database": bool(settings.fabric_default_database),
            "fabric_allowed_workspaces": bool(settings.fabric_allowed_workspaces),
            "fabric_allowed_databases": bool(settings.fabric_allowed_databases),
        },
    }
