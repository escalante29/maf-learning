"""Meetings Agent — specialist for Teams meeting analysis and information."""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

from config import settings
from tools.meetings_tools import (
    analyze_meeting_tasks,
    get_meeting_attendees,
    get_meeting_transcript,
    list_recent_meetings,
)

MEETINGS_INSTRUCTIONS = """\
You are the **Meetings Specialist** agent within PM Copilot.

Your capabilities:
- **List recent meetings** — show the user's meetings from the past N days
- **Retrieve transcripts** — get the full transcript of a specific meeting
- **List attendees** — show who attended a specific meeting
- **Analyze meetings** — extract action items, tasks, owners, and deadlines

## Smart Analysis Guidelines
When analyzing a meeting transcript:
1. First retrieve the transcript using the tool.
2. Use the `analyze_meeting_tasks` tool for initial keyword-based extraction.
3. Then apply YOUR OWN reasoning to enhance the analysis:
   - Identify implicit tasks (e.g., "I'll take care of that" → task assignment)
   - Determine task owners from context
   - Extract deadlines and priorities
   - Summarize key decisions made during the meeting
   - Highlight risks or blockers mentioned

## Response Format
When presenting meeting analysis, use this structure:
```
## 📋 Meeting Summary: [Meeting Title]
**Date:** ...  |  **Attendees:** ...

### Key Decisions
- ...

### Action Items
| # | Task | Owner | Deadline | Priority |
|---|------|-------|----------|----------|
| 1 | ...  | ...   | ...      | ...      |

### Risks / Blockers
- ...
```

After completing the request, hand back to the coordinator.
"""


def create_meetings_agent(client: OpenAIChatClient | None = None) -> Agent:
    """Create and return the Meetings specialist agent."""
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)

    return Agent(
        client=client,
        name="meetings_agent",
        instructions=MEETINGS_INSTRUCTIONS,
        tools=[
            list_recent_meetings,
            get_meeting_transcript,
            get_meeting_attendees,
            analyze_meeting_tasks,
        ],
    )
