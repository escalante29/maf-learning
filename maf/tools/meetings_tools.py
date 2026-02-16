"""Meetings tools — MAF @tool-decorated functions for Teams meeting operations.

Includes transcript retrieval, attendee listing, and AI-powered task extraction.
"""

from __future__ import annotations

import json
from typing import Annotated

from agent_framework import tool

from tools.graph_client import get_graph_client


@tool(approval_mode="never_require")
def list_recent_meetings(
    user_id: Annotated[str, "User principal name or 'me' for the current user"] = "me",
    days_back: Annotated[int, "Number of days to look back for meetings"] = 7,
) -> str:
    """List recent Teams meetings for a user within the specified timeframe."""
    client = get_graph_client()
    meetings = client.list_meetings(user_id, days_back)
    return json.dumps(meetings, indent=2)


@tool(approval_mode="never_require")
def get_meeting_transcript(
    meeting_id: Annotated[str, "The meeting ID to retrieve the transcript for"],
) -> str:
    """Retrieve the full transcript text of a Teams meeting."""
    client = get_graph_client()
    transcript = client.get_transcript(meeting_id)
    return transcript


@tool(approval_mode="never_require")
def get_meeting_attendees(
    meeting_id: Annotated[str, "The meeting ID to get attendees for"],
) -> str:
    """List all attendees of a specific Teams meeting."""
    client = get_graph_client()
    attendees = client.get_attendees(meeting_id)
    return json.dumps(attendees, indent=2)


@tool(approval_mode="never_require")
def analyze_meeting_tasks(
    transcript_text: Annotated[str, "The raw transcript text to analyze for action items"],
) -> str:
    """Analyze a meeting transcript and extract action items, owners, and deadlines.

    This tool uses pattern recognition to identify tasks mentioned in the transcript.
    For deeper AI analysis, the Meetings Agent will use its LLM capabilities directly
    on top of this structured extraction.
    """
    # Basic rule-based extraction — the LLM agent will enhance this with reasoning
    lines = transcript_text.strip().split("\n")
    tasks: list[dict] = []

    task_keywords = [
        "can you", "will do", "i'll", "please", "need to",
        "should", "by ", "deadline", "take the", "handle the",
        "set up", "send", "coordinate", "review", "finish",
        "complete", "deliver", "prepare", "schedule",
    ]

    for line in lines:
        lower = line.lower()
        if any(kw in lower for kw in task_keywords):
            # Try to extract speaker
            speaker = ""
            task_text = line
            if ":" in line:
                parts = line.split(":", 1)
                speaker = parts[0].strip()
                task_text = parts[1].strip()

            tasks.append({
                "speaker": speaker,
                "task": task_text,
                "raw_line": line.strip(),
            })

    result = {
        "total_tasks_found": len(tasks),
        "tasks": tasks,
        "note": (
            "These are preliminary extractions based on keyword matching. "
            "The Meetings Agent will apply AI reasoning for a more complete analysis."
        ),
    }
    return json.dumps(result, indent=2)
