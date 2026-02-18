"""Group Chat Pattern — Workflow: Sprint Planning Debate.

Wires three agents into a GroupChatBuilder with round-robin speaker selection:
  product_owner_agent → tech_lead_agent → scrum_master_agent (repeat)

Run from the maf/ directory:
    python -m agents.04_group_chat.workflow
"""

from __future__ import annotations

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import GroupChatBuilder

from config import settings
from .agents import (
    create_product_owner_agent,
    create_tech_lead_agent,
    create_scrum_master_agent,
)

# ── Colours ──────────────────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
CYAN    = "\033[36m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
MAGENTA = "\033[35m"
BLUE    = "\033[34m"
DIM     = "\033[2m"

AGENT_COLORS = {
    "product_owner_agent": GREEN,
    "tech_lead_agent":     CYAN,
    "scrum_master_agent":  YELLOW,
}

AGENT_LABELS = {
    "product_owner_agent": "🎯 Product Owner",
    "tech_lead_agent":     "🔧 Tech Lead",
    "scrum_master_agent":  "🏃 Scrum Master",
}


def build_sprint_planning_workflow(client: OpenAIChatClient | None = None):
    """Build and return the Group Chat sprint planning workflow."""
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)

    po  = create_product_owner_agent(client)
    tl  = create_tech_lead_agent(client)
    sm  = create_scrum_master_agent(client)

    return (
        GroupChatBuilder(participants=[po, tl, sm])
        .with_max_rounds(3)   # 3 rounds: each agent speaks 3 times
        .build()
    )


async def main():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   💬  MAF Pattern 04 — Group Chat Orchestration              ║
║                                                              ║
║   Example: Sprint Planning Debate                            ║
║   Product Owner ↔ Tech Lead ↔ Scrum Master                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

    workflow = build_sprint_planning_workflow()
    prompt = (
        "Let's plan Sprint 43 for Project Alpha. "
        "We have 6 candidate backlog items (A through F) and need to agree on what to commit. "
        "Remember Sarah starts parental leave mid-sprint, so effective capacity is ~32 pts. "
        "Please debate and agree on the final sprint backlog."
    )

    print(f"{DIM}  Prompt: {prompt[:80]}...{RESET}")
    print(f"{DIM}  Running group chat (3 rounds, round-robin)...{RESET}\n")

    round_num = 0
    last_speaker = None
    events = await workflow.run(prompt)

    for event in events:
        if event.type == "output":
            data = event.data
            messages = []

            if isinstance(data, list):
                messages = data
            elif hasattr(data, "messages"):
                messages = data.messages

            for msg in messages:
                role = getattr(msg, "role", None)
                text = getattr(msg, "text", None)
                speaker = getattr(msg, "author_name", None) or role

                if role != "assistant" or not text:
                    continue

                if speaker != last_speaker:
                    last_speaker = speaker
                    if speaker == "scrum_master_agent":
                        round_num += 1

                color = AGENT_COLORS.get(speaker, MAGENTA)
                label = AGENT_LABELS.get(speaker, speaker)
                print(f"\n{color}{BOLD}  {label}{RESET}")
                for line in text.split("\n"):
                    print(f"  {line}")

    print(f"\n{DIM}  ✅ Group chat sprint planning complete.{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
