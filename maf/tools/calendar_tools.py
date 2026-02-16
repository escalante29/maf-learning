"""Calendar tools — MAF @tool-decorated functions for calendar & scheduling."""

from __future__ import annotations

import json
from typing import Annotated

from agent_framework import tool

from tools.graph_client import get_graph_client


@tool(approval_mode="never_require")
def create_meeting(
    subject: Annotated[str, "Meeting title / subject line"],
    start_time: Annotated[str, "Start time in ISO 8601 format, e.g. '2026-02-20T10:00:00'"],
    end_time: Annotated[str, "End time in ISO 8601 format, e.g. '2026-02-20T11:00:00'"],
    attendees: Annotated[str, "Comma-separated email addresses of attendees"],
) -> str:
    """Create a new calendar event with a Teams meeting link."""
    client = get_graph_client()
    attendee_list = [a.strip() for a in attendees.split(",")]
    result = client.create_event(subject, start_time, end_time, attendee_list)
    return json.dumps(result, indent=2)


@tool(approval_mode="never_require")
def list_upcoming_events(
    user_id: Annotated[str, "User principal name or 'me' for the current user"] = "me",
    days_ahead: Annotated[int, "Number of days to look ahead"] = 7,
) -> str:
    """List upcoming calendar events for a user within the specified timeframe."""
    client = get_graph_client()
    events = client.list_events(user_id, days_ahead)
    return json.dumps(events, indent=2)
