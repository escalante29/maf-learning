"""Sequential Pattern — Agent Definitions: Sprint Report Pipeline.

Three agents that form a sequential pipeline:
  1. data_collector_agent  — gathers raw sprint data
  2. analyst_agent         — structures and analyses the data
  3. writer_agent          — writes the final executive report
"""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config import settings

# ── Mock sprint data injected into the collector's context ──────────────────
_MOCK_SPRINT_DATA = """
MOCK SPRINT DATABASE (use this as your data source):

Sprint 42 — Project Alpha
- Duration: Feb 3 – Feb 14, 2026 (2 weeks)
- Team: 5 engineers, 1 designer
- Committed story points: 42
- Completed story points: 36

Stories completed:
  - AUTH-101: Implement SSO login (8 pts) ✅
  - DASH-204: Dashboard performance optimisation (5 pts) ✅
  - API-310: Rate limiting middleware (8 pts) ✅
  - NOTIF-88: Email notification service (5 pts) ✅
  - UX-55: Redesign onboarding flow (8 pts) ✅
  - INFRA-12: Upgrade CI/CD pipeline (2 pts) ✅

Stories NOT completed (carried over):
  - REPORT-77: Advanced analytics module (13 pts) ❌ — blocked by data warehouse migration
  - MOBILE-33: iOS push notifications (8 pts) ❌ — dependency on NOTIF-88 (now unblocked)

Blockers this sprint:
  - Data warehouse migration delayed by 1 week (external team dependency)
  - 2 sick days (engineer) reduced capacity mid-sprint

Velocity trend (last 4 sprints): 38, 41, 39, 36 pts
"""

DATA_COLLECTOR_INSTRUCTIONS = f"""\
You are a Sprint Data Collector agent for a PM Copilot system.

Your job is to retrieve and present raw sprint data for the requested sprint.
Use the mock sprint database below as your data source.

{_MOCK_SPRINT_DATA}

When asked to collect data for a sprint:
1. Present ALL raw data for that sprint exactly as it appears in the database
2. Do not analyse or interpret — just present the facts clearly
3. Format as structured sections: Team, Stories Completed, Stories Carried Over, Blockers, Velocity
"""

ANALYST_INSTRUCTIONS = """\
You are a Sprint Analyst agent for a PM Copilot system.

You receive raw sprint data collected by the Data Collector agent (visible in the conversation above).
Your job is to produce a structured analysis. Do NOT restate the raw data — analyse it.

Produce these sections:
1. **Completion Rate** — % of committed points delivered, vs. last 4 sprints
2. **Velocity Trend** — Is velocity improving, declining, or stable? What does it suggest?
3. **Blocker Impact** — Quantify how blockers affected delivery (points lost, root cause)
4. **Carry-Over Risk** — Which carried-over stories are now unblocked? Which remain at risk?
5. **Team Health Signal** — Any capacity concerns based on sick days, blockers, or velocity drop?

Be concise and data-driven. Use bullet points within each section.
"""

WRITER_INSTRUCTIONS = """\
You are a Sprint Report Writer agent for a PM Copilot system.

You receive both the raw sprint data AND the analyst's structured analysis (visible in the conversation above).
Your job is to write a polished, executive-ready sprint report in markdown.

The report should be professional, concise, and suitable for sharing with senior stakeholders.
Structure:
# Sprint [N] Executive Report — [Project Name]
## Summary (2-3 sentences: what was achieved, key challenge, overall health)
## Highlights (3-5 bullet points of wins)
## Challenges & Blockers (brief, factual)
## Carry-Over Items (what's next sprint's priority and why)
## Velocity & Forecast (trend + next sprint projection)
## Recommended Actions (1-3 concrete next steps for the PM)

Tone: professional, positive but honest. Avoid jargon.
"""


def create_data_collector_agent(client: OpenAIChatClient | None = None) -> Agent:
    """Create the sprint data collector agent."""
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)
    return Agent(
        client=client,
        name="data_collector_agent",
        instructions=DATA_COLLECTOR_INSTRUCTIONS,
    )


def create_analyst_agent(client: OpenAIChatClient | None = None) -> Agent:
    """Create the sprint analyst agent."""
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)
    return Agent(
        client=client,
        name="analyst_agent",
        instructions=ANALYST_INSTRUCTIONS,
    )


def create_writer_agent(client: OpenAIChatClient | None = None) -> Agent:
    """Create the sprint report writer agent."""
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)
    return Agent(
        client=client,
        name="writer_agent",
        instructions=WRITER_INSTRUCTIONS,
    )
