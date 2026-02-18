"""Concurrent Pattern — Workflow: Project Health Check.

Fans out a health check prompt to 4 independent specialist agents in parallel,
then aggregates their results into a combined health dashboard.

Run from the maf/ directory:
    python -m agents.03_concurrent.workflow
"""

from __future__ import annotations

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import ConcurrentBuilder

from config import settings
from .agents import (
    create_budget_agent,
    create_timeline_agent,
    create_risk_agent,
    create_team_agent,
)

# ── Colours ──────────────────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
CYAN    = "\033[36m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
MAGENTA = "\033[35m"
RED     = "\033[31m"
DIM     = "\033[2m"

AGENT_COLORS = {
    "budget_agent":   GREEN,
    "timeline_agent": CYAN,
    "risk_agent":     RED,
    "team_agent":     YELLOW,
}

AGENT_LABELS = {
    "budget_agent":   "💰 Budget",
    "timeline_agent": "📅 Timeline",
    "risk_agent":     "⚠️  Risks",
    "team_agent":     "👥 Team",
}


def _build_aggregator(agent_names: list[str]):
    """Return a custom aggregator that combines results into a health dashboard."""
    def aggregate(results):
        dashboard = {}
        for i, result in enumerate(results):
            name = agent_names[i] if i < len(agent_names) else f"agent_{i}"
            msgs = result.agent_response.messages if result.agent_response else []
            text = next(
                (m.text for m in reversed(msgs) if getattr(m, "role", None) == "assistant" and m.text),
                "(no response)"
            )
            dashboard[name] = text
        return json.dumps(dashboard, indent=2)
    return aggregate


def build_health_check_workflow(client: OpenAIChatClient | None = None):
    """Build and return the Concurrent health check workflow."""
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)

    budget   = create_budget_agent(client)
    timeline = create_timeline_agent(client)
    risk     = create_risk_agent(client)
    team     = create_team_agent(client)

    agent_names = ["budget_agent", "timeline_agent", "risk_agent", "team_agent"]

    return (
        ConcurrentBuilder(participants=[budget, timeline, risk, team])
        .with_aggregator(_build_aggregator(agent_names))
        .build()
    )


async def main():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ⚡  MAF Pattern 03 — Concurrent Orchestration              ║
║                                                              ║
║   Example: Multi-Domain Project Health Check                 ║
║   budget | timeline | risk | team  (all in parallel)         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

    workflow = build_health_check_workflow()
    prompt = "Perform a full health check for Project Alpha as of today."

    print(f"{DIM}  Prompt: {prompt}{RESET}")
    print(f"{DIM}  Running 4 agents in parallel...{RESET}\n")

    events = await workflow.run(prompt)

    for event in events:
        if event.type == "output":
            data = event.data
            if isinstance(data, str):
                # Our custom aggregator returned JSON
                try:
                    dashboard = json.loads(data)
                    print(f"\n{BOLD}{CYAN}  ═══ PROJECT ALPHA — HEALTH DASHBOARD ═══{RESET}\n")
                    for agent_name, report in dashboard.items():
                        label = AGENT_LABELS.get(agent_name, agent_name)
                        color = AGENT_COLORS.get(agent_name, MAGENTA)
                        print(f"{color}{BOLD}  {label}{RESET}")
                        for line in report.split("\n"):
                            print(f"    {line}")
                        print()
                except json.JSONDecodeError:
                    print(data)
            elif isinstance(data, list):
                # Default aggregator returned list[Message]
                for msg in data:
                    if getattr(msg, "role", None) == "assistant" and msg.text:
                        speaker = getattr(msg, "author_name", None) or "agent"
                        color = AGENT_COLORS.get(speaker, MAGENTA)
                        label = AGENT_LABELS.get(speaker, speaker)
                        print(f"\n{color}{BOLD}  {label}{RESET}")
                        for line in msg.text.split("\n"):
                            print(f"    {line}")

    print(f"\n{DIM}  ✅ Concurrent health check complete.{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
