"""Sequential Pattern — Workflow: Sprint Report Pipeline.

Wires three agents into a SequentialBuilder pipeline:
  data_collector_agent → analyst_agent → writer_agent

Run from the maf/ directory:
    python -m agents.02_sequential.workflow
"""

from __future__ import annotations

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agent_framework import AgentResponse
from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import SequentialBuilder

from config import settings
from .agents import (
    create_data_collector_agent,
    create_analyst_agent,
    create_writer_agent,
)

# ── Colours ──────────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
DIM    = "\033[2m"

AGENT_COLORS = {
    "data_collector_agent": CYAN,
    "analyst_agent": YELLOW,
    "writer_agent": GREEN,
}


def build_sprint_report_workflow(client: OpenAIChatClient | None = None):
    """Build and return the Sequential sprint report pipeline workflow."""
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)

    collector = create_data_collector_agent(client)
    analyst   = create_analyst_agent(client)
    writer    = create_writer_agent(client)

    return SequentialBuilder(participants=[collector, analyst, writer]).build()


async def main():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   📋  MAF Pattern 02 — Sequential Orchestration              ║
║                                                              ║
║   Example: Sprint Report Pipeline                            ║
║   data_collector → analyst → writer                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

    workflow = build_sprint_report_workflow()
    prompt = "Generate a sprint report for Sprint 42 of Project Alpha."

    print(f"{DIM}  Prompt: {prompt}{RESET}")
    print(f"{DIM}  Running sequential pipeline (3 agents)...{RESET}\n")

    events = await workflow.run(prompt)

    for event in events:
        if event.type == "output":
            data = event.data
            if isinstance(data, AgentResponse):
                for msg in data.messages:
                    if not msg.text:
                        continue
                    speaker = msg.author_name or msg.role
                    color = AGENT_COLORS.get(speaker, MAGENTA)
                    print(f"\n{color}{BOLD}  ── {speaker} ──{RESET}")
                    for line in msg.text.split("\n"):
                        print(f"  {line}")
            elif isinstance(data, list):
                # Final conversation snapshot — print the last assistant message
                for msg in reversed(data):
                    if getattr(msg, "role", None) == "assistant" and msg.text:
                        speaker = getattr(msg, "author_name", None) or "writer_agent"
                        color = AGENT_COLORS.get(speaker, GREEN)
                        print(f"\n{color}{BOLD}  ── Final Report ({speaker}) ──{RESET}")
                        for line in msg.text.split("\n"):
                            print(f"  {line}")
                        break

    print(f"\n{DIM}  ✅ Sequential pipeline complete.{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
