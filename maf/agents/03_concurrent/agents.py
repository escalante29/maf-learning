"""Concurrent Pattern — Agent Definitions: Project Health Check.

Four independent specialist agents that analyse different dimensions of project health:
  1. budget_agent    — burn rate vs. plan
  2. timeline_agent  — milestone completion vs. schedule
  3. risk_agent      — open risks and blockers
  4. team_agent      — team capacity and availability
"""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config import settings

# ── Mock project data ────────────────────────────────────────────────────────
_MOCK_PROJECT_DATA = """
PROJECT ALPHA — Status as of Feb 17, 2026

BUDGET:
  - Total budget: $480,000
  - Spent to date: $312,000 (65% of budget)
  - Timeline elapsed: 58% of project duration
  - Budget burn rate: $52,000/month (planned: $48,000/month)
  - Forecast at current rate: $468,000 (within budget, but trending high)
  - Last month overspend: $8,000 (cloud infrastructure costs)

TIMELINE / MILESTONES:
  - Project start: Sep 1, 2025
  - Planned end: Apr 30, 2026
  - Current date: Feb 17, 2026
  - Milestone 1 (MVP): Completed Oct 15, 2025 ✅ (on time)
  - Milestone 2 (Beta): Completed Jan 10, 2026 ✅ (3 days late)
  - Milestone 3 (GA Release): Planned Mar 31, 2026 — AT RISK ⚠️
  - Milestone 4 (Post-launch support): Apr 30, 2026 — TBD
  - Current sprint velocity: 36 pts (planned: 42 pts)

RISKS & BLOCKERS:
  - RISK-01 (HIGH): Data warehouse migration delayed — blocks analytics module (REPORT-77)
    Owner: Infrastructure team | ETA: Feb 28, 2026
  - RISK-02 (MEDIUM): iOS push notification dependency on NOTIF-88 — now unblocked ✅
  - RISK-03 (MEDIUM): Key engineer (Sarah) on parental leave from Mar 1 — 6 weeks
  - RISK-04 (LOW): Third-party payment API deprecation notice — migration needed by Q3
  - Open blockers: 1 active (RISK-01)

TEAM:
  - Team size: 5 engineers, 1 designer, 1 PM
  - Current capacity: 85% (1 engineer part-time due to illness recovery)
  - Upcoming leave: Sarah (engineer, senior) — parental leave Mar 1–Apr 11
  - Planned capacity Mar–Apr: 71% (4.5 FTE engineers)
  - Morale signal: 2 engineers flagged workload concerns in last retrospective
  - Hiring: 1 junior engineer onboarding Feb 24 (ramp-up: 3–4 weeks)
"""

BUDGET_INSTRUCTIONS = f"""\
You are a Budget Health Analyst for a PM Copilot system.

Analyse ONLY the budget health of the project. Use the project data below.

{_MOCK_PROJECT_DATA}

Produce a concise budget health assessment:
- Current spend vs. plan (% and absolute)
- Burn rate trend (on track / over / under)
- Forecast to completion
- Key budget risk (if any)
- Overall budget health: 🟢 HEALTHY / 🟡 AT RISK / 🔴 CRITICAL

Be concise — 5-8 bullet points maximum.
"""

TIMELINE_INSTRUCTIONS = f"""\
You are a Timeline Health Analyst for a PM Copilot system.

Analyse ONLY the timeline and milestone health of the project. Use the project data below.

{_MOCK_PROJECT_DATA}

Produce a concise timeline health assessment:
- Milestones completed vs. planned (on time / late)
- Current sprint velocity vs. plan
- Upcoming milestone risk assessment
- Projected completion date vs. planned
- Overall timeline health: 🟢 ON TRACK / 🟡 AT RISK / 🔴 DELAYED

Be concise — 5-8 bullet points maximum.
"""

RISK_INSTRUCTIONS = f"""\
You are a Risk & Blocker Analyst for a PM Copilot system.

Analyse ONLY the risks and blockers for the project. Use the project data below.

{_MOCK_PROJECT_DATA}

Produce a concise risk assessment:
- Active blockers (count, severity, ETA to resolution)
- Top 3 risks ranked by impact
- Risks that have been resolved recently
- Recommended immediate actions for the PM
- Overall risk level: 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH

Be concise — 5-8 bullet points maximum.
"""

TEAM_INSTRUCTIONS = f"""\
You are a Team Health Analyst for a PM Copilot system.

Analyse ONLY the team capacity and health for the project. Use the project data below.

{_MOCK_PROJECT_DATA}

Produce a concise team health assessment:
- Current capacity vs. planned
- Upcoming capacity changes (leave, onboarding)
- Morale and workload signals
- Impact of capacity changes on upcoming milestones
- Overall team health: 🟢 HEALTHY / 🟡 STRAINED / 🔴 CRITICAL

Be concise — 5-8 bullet points maximum.
"""


def create_budget_agent(client: OpenAIChatClient | None = None) -> Agent:
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)
    return Agent(client=client, name="budget_agent", instructions=BUDGET_INSTRUCTIONS)


def create_timeline_agent(client: OpenAIChatClient | None = None) -> Agent:
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)
    return Agent(client=client, name="timeline_agent", instructions=TIMELINE_INSTRUCTIONS)


def create_risk_agent(client: OpenAIChatClient | None = None) -> Agent:
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)
    return Agent(client=client, name="risk_agent", instructions=RISK_INSTRUCTIONS)


def create_team_agent(client: OpenAIChatClient | None = None) -> Agent:
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)
    return Agent(client=client, name="team_agent", instructions=TEAM_INSTRUCTIONS)
