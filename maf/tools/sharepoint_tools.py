"""SharePoint tools — MAF @tool-decorated functions for SharePoint operations."""

from __future__ import annotations

import json
from typing import Annotated

from agent_framework import tool

from tools.graph_client import get_graph_client


@tool(approval_mode="never_require")
def list_sharepoint_sites() -> str:
    """List all SharePoint sites available in the organisation."""
    client = get_graph_client()
    sites = client.list_sites()
    return json.dumps(sites, indent=2)


@tool(approval_mode="never_require")
def create_sharepoint_site(
    name: Annotated[str, "Display name for the new SharePoint site"],
    description: Annotated[str, "Description of the site's purpose"],
) -> str:
    """Create a new SharePoint team site with the given name and description."""
    client = get_graph_client()
    result = client.create_site(name, description)
    return json.dumps(result, indent=2)


@tool(approval_mode="never_require")
def create_sharepoint_list(
    site_id: Annotated[str, "The SharePoint site ID to create the list in"],
    list_name: Annotated[str, "Name of the new list"],
    columns: Annotated[str, "Comma-separated column names, e.g. 'Title,Status,Assignee,DueDate'"],
) -> str:
    """Create a new list on a SharePoint site with the specified columns."""
    client = get_graph_client()
    column_list = [c.strip() for c in columns.split(",")]
    result = client.create_list(site_id, list_name, column_list)
    return json.dumps(result, indent=2)


@tool(approval_mode="never_require")
def upload_to_sharepoint(
    site_id: Annotated[str, "The SharePoint site ID"],
    folder_path: Annotated[str, "Destination folder path, e.g. 'Shared Documents/Reports'"],
    file_name: Annotated[str, "Name of the file to upload"],
) -> str:
    """Upload a file to a SharePoint document library folder."""
    client = get_graph_client()
    result = client.upload_file(site_id, folder_path, file_name)
    return json.dumps(result, indent=2)
