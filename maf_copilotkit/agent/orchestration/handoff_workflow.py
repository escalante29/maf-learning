"""Handoff Workflow — wires agents into the MAF HandoffBuilder.

Creates a Handoff orchestration connecting the Triage coordinator
to specialist agents in a star topology.
"""

from __future__ import annotations

from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import HandoffBuilder

from agents.triage_agent import create_triage_agent
from agents.task_agent import create_task_agent
from agents.calendar_agent import create_calendar_agent
from config import settings


def build_workflow(thread_id: str | None = None, client: OpenAIChatClient | None = None):
    """Build and return the PM Copilot Handoff workflow.

    Architecture:
        User → Triage (coordinator)
        Triage → Task | Calendar
        Each specialist → Triage (hand back after completing task)

    Args:
        thread_id: Optional thread ID passed by the AG-UI workflow factory.
        client: Optional shared OpenAIChatClient. If None, one is created
                using the OpenAI API key from settings.

    Returns:
        A built HandoffBuilder workflow ready for `.run()`.
    """
    if client is None:
        client = OpenAIChatClient(model_id="gpt-4o", api_key=settings.openai_api_key)

    # ── Create all agents with the shared client ─────────────────────
    triage = create_triage_agent(client)
    task = create_task_agent(client)
    calendar = create_calendar_agent(client)

    specialists = [task, calendar]

    # ── Build the Handoff workflow ───────────────────────────────────
    workflow = (
        HandoffBuilder(
            name="pm_copilot",
            participants=[triage, *specialists],
        )
        .with_start_agent(triage)
        # Triage can route to any specialist
        .add_handoff(triage, specialists)
        # Each specialist can hand back to triage
        .add_handoff(task, [triage])
        .add_handoff(calendar, [triage])
        .build()
    )

    return workflow
