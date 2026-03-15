"""Mock calendar tools for the Calendar Agent."""

from __future__ import annotations

import json
from typing import Annotated

from agent_framework import tool


@tool(approval_mode="never_require")
def list_upcoming_events(days: Annotated[int, "Number of days to look ahead"] = 7) -> str:
    """List upcoming calendar events for the next N days.

    Args:
        days: Number of days to look ahead (default: 7).

    Returns:
        JSON string with event data.
    """
    events = [
        {
            "subject": "Sprint Planning — Project Alpha",
            "date": "2026-03-17",
            "time": "09:00 AM",
            "duration": "1 hour",
            "organizer": "Alice Chen",
            "teams_link": "https://teams.microsoft.com/l/meetup-join/example1",
        },
        {
            "subject": "Architecture Review",
            "date": "2026-03-18",
            "time": "02:00 PM",
            "duration": "45 minutes",
            "organizer": "Bob Martinez",
            "teams_link": "https://teams.microsoft.com/l/meetup-join/example2",
        },
        {
            "subject": "1:1 with Manager",
            "date": "2026-03-19",
            "time": "10:30 AM",
            "duration": "30 minutes",
            "organizer": "Carol Singh",
            "teams_link": "https://teams.microsoft.com/l/meetup-join/example3",
        },
        {
            "subject": "All-Hands Town Hall",
            "date": "2026-03-20",
            "time": "04:00 PM",
            "duration": "1 hour",
            "organizer": "Leadership Team",
            "teams_link": "https://teams.microsoft.com/l/meetup-join/example4",
        },
    ]

    return json.dumps(
        {"days_ahead": days, "total": len(events), "events": events},
        indent=2,
    )


@tool(approval_mode="never_require")
def create_meeting(
    subject: Annotated[str, "Meeting subject/title"],
    date: Annotated[str, "Date in YYYY-MM-DD format"],
    time: Annotated[str, "Time e.g. '2:00 PM'"],
    duration: Annotated[str, "Duration string e.g. '1 hour'"] = "1 hour",
    attendees: Annotated[str, "Comma-separated email addresses"] = "",
) -> str:
    """Create a new calendar event with a Teams meeting link.

    Args:
        subject: Meeting subject/title.
        date: Date in YYYY-MM-DD format.
        time: Time (e.g. "2:00 PM").
        duration: Duration string (default: "1 hour").
        attendees: Comma-separated email addresses.

    Returns:
        JSON string confirming the created meeting.
    """
    attendee_list = [a.strip() for a in attendees.split(",") if a.strip()]

    meeting = {
        "status": "created",
        "subject": subject,
        "date": date,
        "time": time,
        "duration": duration,
        "attendees": attendee_list or ["(no attendees specified)"],
        "teams_link": "https://teams.microsoft.com/l/meetup-join/new-meeting-id",
        "meeting_id": "MTG-20260317-001",
    }

    return json.dumps(meeting, indent=2)
