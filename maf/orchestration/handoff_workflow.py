"""Handoff Workflow — wires all agents into the MAF HandoffBuilder.

This module creates the Handoff orchestration that connects the Triage
coordinator agent to all specialist agents in a star topology.
"""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import HandoffBuilder

from agents.calendar_agent import create_calendar_agent
from agents.documents_agent import create_documents_agent
from agents.meetings_agent import create_meetings_agent
from agents.project_info_agent import create_project_info_agent
from agents.sharepoint_agent import create_sharepoint_agent
from agents.triage import create_triage_agent
from config import settings


def build_pm_workflow(client: OpenAIChatClient | None = None):
    """Build and return the PM Assistant Handoff workflow.

    Architecture:
        User → Triage (coordinator)
        Triage → SharePoint | Meetings | Calendar | Documents | ProjectInfo
        Each specialist → Triage (hand back after completing task)

    Args:
        client: Optional shared OpenAIChatClient. If None, one is created
                using the OpenAI API key from settings.

    Returns:
        A built HandoffBuilder workflow ready for `.run()`.
    """
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)

    # ── Create all agents with the shared client ─────────────────────
    triage = create_triage_agent(client)
    sharepoint = create_sharepoint_agent(client)
    meetings = create_meetings_agent(client)
    calendar = create_calendar_agent(client)
    documents = create_documents_agent(client)
    project_info = create_project_info_agent(client)

    specialists = [sharepoint, meetings, calendar, documents, project_info]

    # ── Build the Handoff workflow ───────────────────────────────────
    workflow = (
        HandoffBuilder(
            name="pm_copilot",
            participants=[triage, *specialists],
            # Terminate when the user says goodbye or a similar farewell
            termination_condition=lambda conv: (
                len(conv) > 0
                and conv[-1].role == "user"
                and any(
                    phrase in conv[-1].text.lower()
                    for phrase in [
                        "goodbye", "bye", "that's all", "thank you",
                        "thanks, that's it", "nothing else", "exit", "quit",
                    ]
                )
            ),
        )
        .with_start_agent(triage)
        # Triage can route to any specialist
        .add_handoff(triage, specialists)
        # Each specialist can hand back to triage
        .add_handoff(sharepoint, [triage])
        .add_handoff(meetings, [triage])
        .add_handoff(calendar, [triage])
        .add_handoff(documents, [triage])
        .add_handoff(project_info, [triage])
        .build()
    )

    return workflow
