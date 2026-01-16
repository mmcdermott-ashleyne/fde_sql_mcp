from __future__ import annotations

import asyncio
import sys
from typing import Any, Dict, List

from mcp.server.fastmcp import FastMCP

from .tools import databases as DB

# -----------------------------------------------------------------------------
# MCP Server Setup
# -----------------------------------------------------------------------------
mcp = FastMCP("FDE SQL MCP", json_response=True)


# -----------------------------------------------------------------------------
# Utility Tools
# -----------------------------------------------------------------------------
@mcp.tool(description="Health check to verify the MCP server is running.")
async def ping() -> str:
    return "pong"


# -----------------------------------------------------------------------------
# SQL Server Tools
# -----------------------------------------------------------------------------
@mcp.tool(
    description=(
        "List databases visible to the current Windows-authenticated user "
        "on the configured SQL Server instance."
    )
)
async def list_databases() -> List[Dict[str, Any]]:
    return await asyncio.to_thread(DB.list_databases_impl)


@mcp.tool(
    description=(
        "List tables in the specified database. Returns schema, table name, "
        "and creation/modification metadata."
    )
)
async def list_tables(database: str) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(DB.list_tables_impl, database)


@mcp.tool(
    description=("List views in the specified database along with schema and timestamps.")
)
async def list_views(database: str) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(DB.list_views_impl, database)


@mcp.tool(
    description=("List stored procedures in the specified database with metadata.")
)
async def list_stored_procedures(database: str) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(DB.list_stored_procedures_impl, database)


@mcp.tool(
    description=("List indexes for tables in the specified database.")
)
async def list_indexes(database: str) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(DB.list_indexes_impl, database)


# -----------------------------------------------------------------------------
# Entrypoint (stdio)
# -----------------------------------------------------------------------------
def run() -> None:
    """
    Start the FDE SQL MCP server over stdio.
    This will block and serve tool requests until terminated.
    """
    print("Starting FDE SQL MCP server...", file=sys.stderr, flush=True)
    mcp.run()


if __name__ == "__main__":
    run()
