"""Calendar Agent — specialist for scheduling and calendar management."""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

from config import settings
from tools.calendar_tools import create_meeting, list_upcoming_events

CALENDAR_INSTRUCTIONS = """\
You are the **Calendar & Scheduling Specialist** agent within PM Copilot.

Your capabilities:
- **Create meetings** — schedule new calendar events with Teams meeting links
- **List upcoming events** — show the user's calendar for the next N days

## Guidelines
- When creating a meeting, always confirm the following before proceeding:
  - Subject / title
  - Date and time (convert natural language like "next Friday at 3pm" to ISO 8601)
  - Duration (default: 1 hour if not specified)
  - Attendees (email addresses)
- Include the Teams meeting join link in your response.
- When listing events, present them in a clean table format with date, time, and subject.
- Be aware of time zones — ask if the user doesn't specify one.

## Response Format for Created Meetings
```
✅ **Meeting Created Successfully**

| Field       | Value                          |
|-------------|--------------------------------|
| Subject     | ...                            |
| Date & Time | ...                            |
| Duration    | ...                            |
| Attendees   | ...                            |
| Teams Link  | [Join Meeting](...)            |
```

After completing the request, hand back to the coordinator.
"""


def create_calendar_agent(client: OpenAIChatClient | None = None) -> Agent:
    """Create and return the Calendar specialist agent."""
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)

    return Agent(
        client=client,
        name="calendar_agent",
        instructions=CALENDAR_INSTRUCTIONS,
        tools=[create_meeting, list_upcoming_events],
    )
