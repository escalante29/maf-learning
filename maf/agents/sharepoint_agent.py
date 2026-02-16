"""SharePoint Agent — specialist for SharePoint operations."""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

from config import settings
from tools.sharepoint_tools import (
    create_sharepoint_list,
    create_sharepoint_site,
    list_sharepoint_sites,
    upload_to_sharepoint,
)

SHAREPOINT_INSTRUCTIONS = """\
You are the **SharePoint Specialist** agent within PM Copilot.

Your capabilities:
- **List** existing SharePoint sites in the organization
- **Create** new SharePoint team sites with a name and description
- **Create lists** on SharePoint sites with custom columns (e.g., task boards, trackers)
- **Upload files** to SharePoint document libraries

## Guidelines
- Always confirm the site name / list name before creating resources.
- When creating a list, suggest useful columns if the user doesn't specify them \
(e.g., Title, Status, Assignee, Due Date, Priority for a task tracker).
- Provide the SharePoint URL in your response so the user can navigate directly.
- After completing the request, hand back to the coordinator so the user can \
make additional requests.
"""


def create_sharepoint_agent(client: OpenAIChatClient | None = None) -> Agent:
    """Create and return the SharePoint specialist agent."""
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)

    return Agent(
        client=client,
        name="sharepoint_agent",
        instructions=SHAREPOINT_INSTRUCTIONS,
        tools=[
            list_sharepoint_sites,
            create_sharepoint_site,
            create_sharepoint_list,
            upload_to_sharepoint,
        ],
    )
