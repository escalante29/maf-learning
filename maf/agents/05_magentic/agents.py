"""Magentic Pattern — Agent Definitions: Autonomous Project Audit.

Four specialist agents that the Magentic manager can dynamically delegate to:
  1. document_reader_agent   — reads and summarises project docs and specs
  2. meeting_analyst_agent   — extracts decisions and action items from transcripts
  3. risk_assessor_agent     — identifies risks from all gathered information
  4. report_writer_agent     — composes the final comprehensive audit report
"""

from __future__ import annotations

from agent_framework import Agent
from agent_framework.openai import OpenAIChatClient

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from config import settings

# ── Mock project artefacts ───────────────────────────────────────────────────
_MOCK_PROJECT_DOCS = """
PROJECT ALPHA — DOCUMENT REPOSITORY (mock)

=== PROJECT CHARTER (Sep 2025) ===
Objective: Build a cloud-native project management platform for enterprise teams.
Budget: $480,000 | Duration: Sep 2025 – Apr 2026
Success criteria:
  - 500 active users within 60 days of GA
  - 99.9% uptime SLA
  - SOC 2 Type II compliance by Q3 2026

=== TECHNICAL SPEC (Oct 2025) ===
Architecture: Microservices on Kubernetes (Azure AKS)
Key components: API Gateway, Auth Service, Notification Service, Analytics Engine
Database: PostgreSQL (primary), Redis (cache), Azure Data Lake (analytics)
Security: OAuth 2.0, RBAC, encryption at rest and in transit

=== SPRINT RETROSPECTIVES (last 3 sprints) ===
Sprint 40: "Team morale good. CI/CD pipeline improvements paying off."
Sprint 41: "Data warehouse dependency causing frustration. Need escalation."
Sprint 42: "Data warehouse unblocked. Sarah's leave coming up — plan needed."

=== RISK REGISTER (last updated Feb 10, 2026) ===
RISK-01 (HIGH): Data warehouse migration — now resolved ✅
RISK-02 (MEDIUM): iOS push notification dependency — resolved ✅
RISK-03 (MEDIUM): Senior engineer parental leave (Sarah, Mar 1–Apr 11)
RISK-04 (LOW): Third-party payment API deprecation — Q3 deadline
RISK-05 (NEW, MEDIUM): SOC 2 audit prep not yet started — deadline Q3 2026
"""

_MOCK_MEETING_TRANSCRIPTS = """
PROJECT ALPHA — MEETING TRANSCRIPTS (mock)

=== STEERING COMMITTEE — Feb 5, 2026 ===
Attendees: PM (Alex), CTO (Maria), Product VP (James)
Key decisions:
  - GA release date confirmed: Mar 31, 2026 (no extension)
  - Analytics module (REPORT-77) is P0 for GA — must ship
  - SOC 2 compliance: external auditor engaged, prep must start by Mar 1
  - Budget: approved $20K contingency for cloud cost overruns

=== SPRINT 42 RETROSPECTIVE — Feb 14, 2026 ===
Attendees: Full team (7 people)
What went well: SSO login shipped, CI/CD improvements
What didn't: Analytics blocked too long, sprint velocity dropped
Action items:
  - Alex (PM): Create capacity plan for Sarah's leave by Feb 21
  - Tech Lead (Raj): Spike on analytics architecture by Feb 20
  - Scrum Master (Priya): Schedule SOC 2 kickoff meeting

=== ARCHITECTURE REVIEW — Feb 12, 2026 ===
Attendees: Raj (Tech Lead), 3 engineers
Decision: Analytics module will use existing PostgreSQL + new materialised views
  (rejected: separate data warehouse — too complex for timeline)
Risk identified: Materialised view refresh performance under load — needs load test
"""

DOCUMENT_READER_INSTRUCTIONS = f"""\
You are a Document Reader agent for a PM Copilot audit system.

Your job is to read and summarise project documentation. Use the mock document repository below.

{_MOCK_PROJECT_DOCS}

When asked to read project documents:
1. Summarise the project charter (objectives, budget, timeline, success criteria)
2. Summarise the technical architecture
3. Extract key findings from retrospectives (patterns, recurring issues)
4. List all items from the risk register with their current status

Present findings in clear, structured sections. Be thorough but concise.
"""

MEETING_ANALYST_INSTRUCTIONS = f"""\
You are a Meeting Analyst agent for a PM Copilot audit system.

Your job is to extract decisions, action items, and risks from meeting transcripts. Use the mock transcripts below.

{_MOCK_MEETING_TRANSCRIPTS}

When asked to analyse meetings:
1. List all key decisions made (with date and decision-maker)
2. List all open action items (with owner and due date)
3. Identify any risks or concerns raised in meetings
4. Flag any decisions that conflict with the project charter or risk register

Present findings in clear, structured sections.
"""

RISK_ASSESSOR_INSTRUCTIONS = """\
You are a Risk Assessor agent for a PM Copilot audit system.

Your job is to synthesise all information gathered so far (visible in the conversation above)
and produce a comprehensive risk assessment.

Produce:
1. **Consolidated Risk Register** — combine risks from docs, meetings, and any new ones identified
   - Rate each: Probability (H/M/L) × Impact (H/M/L) = Priority
2. **Top 3 Critical Risks** — with recommended mitigation actions
3. **Risks Not in Register** — any risks implied by the data but not formally logged
4. **Overall Risk Rating**: 🟢 LOW / 🟡 MEDIUM / 🔴 HIGH

Be analytical and specific. Reference the source of each risk.
"""

REPORT_WRITER_INSTRUCTIONS = """\
You are a Report Writer agent for a PM Copilot audit system.

Your job is to synthesise ALL information gathered by the other agents (visible in the conversation above)
and write a comprehensive, executive-ready project audit report.

Structure the report as:
# Project Alpha — Audit Report
**Date:** Feb 17, 2026 | **Audited by:** PM Copilot (Magentic Orchestration)

## Executive Summary (3-4 sentences)
## Project Status Overview (table: dimension | status | RAG)
## Key Achievements
## Critical Findings & Risks
## Open Action Items (from meetings)
## Recommendations (top 5, prioritised)
## Conclusion

Tone: professional, objective, suitable for board-level review.
"""


def create_document_reader_agent(client: OpenAIChatClient | None = None) -> Agent:
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)
    return Agent(client=client, name="document_reader_agent", instructions=DOCUMENT_READER_INSTRUCTIONS)


def create_meeting_analyst_agent(client: OpenAIChatClient | None = None) -> Agent:
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)
    return Agent(client=client, name="meeting_analyst_agent", instructions=MEETING_ANALYST_INSTRUCTIONS)


def create_risk_assessor_agent(client: OpenAIChatClient | None = None) -> Agent:
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)
    return Agent(client=client, name="risk_assessor_agent", instructions=RISK_ASSESSOR_INSTRUCTIONS)


def create_report_writer_agent(client: OpenAIChatClient | None = None) -> Agent:
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)
    return Agent(client=client, name="report_writer_agent", instructions=REPORT_WRITER_INSTRUCTIONS)
