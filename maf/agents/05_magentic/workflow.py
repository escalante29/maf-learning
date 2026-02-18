"""Magentic Pattern — Workflow: Autonomous Project Audit.

The Magentic manager dynamically plans and delegates to specialist agents:
  document_reader_agent, meeting_analyst_agent, risk_assessor_agent, report_writer_agent

Run from the maf/ directory:
    python -m agents.05_magentic.workflow
"""

from __future__ import annotations

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agent_framework.openai import OpenAIChatClient
from agent_framework.orchestrations import MagenticBuilder

from config import settings
from .agents import (
    create_document_reader_agent,
    create_meeting_analyst_agent,
    create_risk_assessor_agent,
    create_report_writer_agent,
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
    "document_reader_agent": CYAN,
    "meeting_analyst_agent": YELLOW,
    "risk_assessor_agent":   MAGENTA,
    "report_writer_agent":   GREEN,
    "magentic_manager":      BLUE,
}

AGENT_LABELS = {
    "document_reader_agent": "📄 Document Reader",
    "meeting_analyst_agent": "🗣️  Meeting Analyst",
    "risk_assessor_agent":   "⚠️  Risk Assessor",
    "report_writer_agent":   "📝 Report Writer",
    "magentic_manager":      "🧠 Magentic Manager",
}


def build_project_audit_workflow(client: OpenAIChatClient | None = None):
    """Build and return the Magentic project audit workflow."""
    if client is None:
        client = OpenAIChatClient(api_key=settings.openai_api_key)

    doc_reader      = create_document_reader_agent(client)
    meeting_analyst = create_meeting_analyst_agent(client)
    risk_assessor   = create_risk_assessor_agent(client)
    report_writer   = create_report_writer_agent(client)

    return (
        MagenticBuilder(
            participants=[doc_reader, meeting_analyst, risk_assessor, report_writer]
        )
        .build()
    )


async def main():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🧠  MAF Pattern 05 — Magentic Orchestration                ║
║                                                              ║
║   Example: Autonomous Project Audit                          ║
║   Manager dynamically delegates to specialist agents         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

    workflow = build_project_audit_workflow()
    prompt = (
        "Perform a comprehensive end-to-end audit of Project Alpha. "
        "Review all project documentation, analyse meeting transcripts, "
        "assess all risks, and produce a complete audit report suitable for "
        "executive review."
    )

    print(f"{DIM}  Prompt: {prompt[:80]}...{RESET}")
    print(f"{DIM}  Running Magentic manager (adaptive planning)...{RESET}\n")
    print(f"{DIM}  Note: The manager will dynamically decide which agents to call and in what order.{RESET}\n")

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
                role    = getattr(msg, "role", None)
                text    = getattr(msg, "text", None)
                speaker = getattr(msg, "author_name", None) or role

                if role != "assistant" or not text:
                    continue
                if speaker == last_speaker:
                    continue
                last_speaker = speaker

                color = AGENT_COLORS.get(speaker, MAGENTA)
                label = AGENT_LABELS.get(speaker, speaker)
                print(f"\n{color}{BOLD}  ── {label} ──{RESET}")
                for line in text.split("\n"):
                    print(f"  {line}")

    print(f"\n{DIM}  ✅ Magentic audit complete.{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
