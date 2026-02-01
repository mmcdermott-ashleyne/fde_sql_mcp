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


@mcp.tool(
    description=(
        "Run a validated, read-only SELECT query with row limits enforced."
    )
)
async def run_readonly_query(
    database: str, query: str, max_rows: int | None = None
) -> Dict[str, Any]:
    return await asyncio.to_thread(
        DB.run_readonly_query_impl, database, query, max_rows
    )


@mcp.tool(
    description=(
        "List columns for a table in the specified database (schema required)."
    )
)
async def list_table_columns(
    database: str, schema: str, table: str
) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(
        DB.list_table_columns_impl, database, schema, table
    )


@mcp.tool(
    description=(
        "List columns for a view in the specified database (schema required)."
    )
)
async def list_view_columns(
    database: str, schema: str, view: str
) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(
        DB.list_view_columns_impl, database, schema, view
    )


@mcp.tool(
    description=(
        "List primary key and unique constraints for a table (schema required)."
    )
)
async def list_table_constraints(
    database: str, schema: str, table: str
) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(
        DB.list_table_constraints_impl, database, schema, table
    )


@mcp.tool(
    description=("List foreign key relationships for a table.")
)
async def list_foreign_keys(
    database: str, schema: str, table: str
) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(
        DB.list_foreign_keys_impl, database, schema, table
    )


@mcp.tool(
    description=(
        "List index definitions for a table including key/include columns."
    )
)
async def list_index_details(
    database: str, schema: str, table: str
) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(
        DB.list_index_details_impl, database, schema, table
    )


@mcp.tool(
    description=("Return the SQL definition of a view.")
)
async def list_view_definition(
    database: str, schema: str, view: str
) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(
        DB.list_view_definition_impl, database, schema, view
    )


@mcp.tool(
    description=("Return the SQL definition of a stored procedure.")
)
async def list_stored_procedure_definition(
    database: str, schema: str, procedure: str
) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(
        DB.list_stored_procedure_definition_impl, database, schema, procedure
    )


@mcp.tool(
    description=("List parameters for a stored procedure.")
)
async def list_stored_procedure_parameters(
    database: str, schema: str, procedure: str
) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(
        DB.list_stored_procedure_parameters_impl, database, schema, procedure
    )


@mcp.tool(
    description=("List referenced objects for a view or stored procedure.")
)
async def list_object_dependencies(
    database: str, schema: str, object_name: str
) -> List[Dict[str, Any]]:
    return await asyncio.to_thread(
        DB.list_object_dependencies_impl, database, schema, object_name
    )


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
