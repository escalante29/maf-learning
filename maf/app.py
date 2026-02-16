"""PM Copilot — Main entry point.

Usage:
    # Console mode (interactive terminal)
    python app.py --console

    # Bot webhook server (for MS Teams)
    python app.py --server

    # MAF DevUI mode (visual debugging)
    python app.py --devui

Environment:
    Copy .env.example to .env and fill in your OpenAI API key.
    Set GRAPH_MODE=mock for demo mode (no Azure credentials needed).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from typing import cast

from agent_framework import AgentResponse, Message, WorkflowRunState
from agent_framework.orchestrations import HandoffAgentUserRequest

from orchestration.handoff_workflow import build_pm_workflow

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s │ %(name)-25s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("pm_copilot")
logger.setLevel(logging.INFO)

# ═══════════════════════════════════════════════════════════════════════════
# Colours for terminal output
# ═══════════════════════════════════════════════════════════════════════════
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
DIM = "\033[2m"


def _agent_color(name: str) -> str:
    """Return a consistent colour for a given agent name."""
    colors = {
        "triage_agent": CYAN,
        "sharepoint_agent": "\033[34m",    # blue
        "meetings_agent": MAGENTA,
        "calendar_agent": GREEN,
        "documents_agent": YELLOW,
        "project_info_agent": "\033[96m",  # bright cyan
    }
    return colors.get(name, CYAN)


# ═══════════════════════════════════════════════════════════════════════════
# Event handler (reusable across modes)
# ═══════════════════════════════════════════════════════════════════════════

def handle_events(events: list) -> list:
    """Process workflow events and return any pending user-input requests."""
    requests = []

    for event in events:
        if event.type == "handoff_sent":
            source = event.data.source
            target = event.data.target
            print(
                f"\n{DIM}  ↳ Handoff: {source} → {target}{RESET}"
            )

        elif event.type == "status" and event.state in {
            WorkflowRunState.IDLE,
            WorkflowRunState.IDLE_WITH_PENDING_REQUESTS,
        }:
            pass  # Suppress noisy status events in console

        elif event.type == "output":
            data = event.data
            if isinstance(data, AgentResponse):
                for message in data.messages:
                    if not message.text:
                        continue
                    speaker = message.author_name or message.role
                    color = _agent_color(speaker)
                    print(f"\n{color}{BOLD}  🤖 {speaker}:{RESET}")
                    # Indent the message
                    for line in message.text.split("\n"):
                        print(f"  {line}")
            elif isinstance(data, list):
                # Final conversation snapshot — suppress for cleanliness
                pass

        elif event.type == "request_info" and isinstance(
            event.data, HandoffAgentUserRequest
        ):
            response = event.data.agent_response
            if response and response.messages:
                for message in response.messages:
                    if not message.text:
                        continue
                    speaker = message.author_name or message.role
                    color = _agent_color(speaker)
                    print(f"\n{color}{BOLD}  🤖 {speaker}:{RESET}")
                    for line in message.text.split("\n"):
                        print(f"  {line}")
            requests.append(event)

    return requests


# ═══════════════════════════════════════════════════════════════════════════
# Console Mode
# ═══════════════════════════════════════════════════════════════════════════

async def run_console():
    """Interactive terminal conversation with PM Copilot."""
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🤖  PM Copilot — AI Project Manager Assistant              ║
║                                                              ║
║   Powered by Microsoft Agent Framework (Handoff Pattern)     ║
║   Type your message and press Enter. Type 'quit' to exit.    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

    workflow = build_pm_workflow()

    # Get initial message from user
    user_input = input(f"{GREEN}{BOLD}  👤 You: {RESET}").strip()
    if not user_input or user_input.lower() in ("quit", "exit", "q"):
        print(f"\n{DIM}  Goodbye! 👋{RESET}\n")
        return

    # Start the workflow
    print(f"\n{DIM}  ⏳ Processing...{RESET}")
    result = workflow.run(user_input, stream=True)
    pending = handle_events([event async for event in result])

    # Conversation loop
    while pending:
        print()
        user_input = input(f"{GREEN}{BOLD}  👤 You: {RESET}").strip()

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            responses = {
                req.request_id: HandoffAgentUserRequest.terminate()
                for req in pending
            }
        else:
            responses = {
                req.request_id: HandoffAgentUserRequest.create_response(user_input)
                for req in pending
            }

        print(f"\n{DIM}  ⏳ Processing...{RESET}")
        events = await workflow.run(responses=responses)
        pending = handle_events(events)

    print(f"\n{DIM}  ✅ Conversation ended. Goodbye! 👋{RESET}\n")


# ═══════════════════════════════════════════════════════════════════════════
# Server Mode (Bot Framework webhook — placeholder)
# ═══════════════════════════════════════════════════════════════════════════

async def run_server():
    """Start the FastAPI server for MS Teams Bot webhook."""
    try:
        import uvicorn
        from fastapi import FastAPI, Request
        from fastapi.responses import JSONResponse
    except ImportError:
        print("FastAPI/uvicorn not installed. Run: pip install fastapi uvicorn[standard]")
        sys.exit(1)

    from config import settings

    app = FastAPI(
        title="PM Copilot Bot",
        description="AI Project Manager Assistant — MS Teams Bot Webhook",
        version="1.0.0",
    )

    @app.get("/")
    async def root():
        return {"status": "ok", "service": "PM Copilot Bot", "mode": settings.graph_mode}

    @app.post("/api/messages")
    async def messages(request: Request):
        """Bot Framework webhook endpoint — receives activity from Teams."""
        # TODO: Wire to BotFrameworkAdapter + TeamsBot activity handler
        body = await request.json()
        logger.info("Received activity: %s", body.get("type", "unknown"))
        return JSONResponse(content={"status": "received"}, status_code=200)

    port = settings.port
    print(f"\n{CYAN}{BOLD}  🚀 PM Copilot Bot server starting on port {port}...{RESET}")
    print(f"  Webhook URL: http://localhost:{port}/api/messages\n")

    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


# ═══════════════════════════════════════════════════════════════════════════
# DevUI Mode (MAF built-in developer UI)
# ═══════════════════════════════════════════════════════════════════════════

async def run_devui():
    """Launch MAF DevUI for visual debugging of the agent workflow."""
    print(f"""
{MAGENTA}{BOLD}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🔬  PM Copilot — DevUI Mode                                ║
║                                                              ║
║   Launching the MAF Developer UI for visual workflow          ║
║   debugging. The browser should open automatically.           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

    try:
        from agent_framework.dev_ui import DevUI
    except ImportError:
        print(
            f"{YELLOW}  ⚠️  DevUI is not available in your MAF installation.{RESET}\n"
            "  This feature requires additional MAF packages.\n"
            "  Try: pip install agent-framework[devui] --pre\n"
            "\n"
            f"  Falling back to console mode...\n"
        )
        await run_console()
        return

    workflow = build_pm_workflow()

    # Launch DevUI with the workflow
    dev_ui = DevUI(workflow)
    await dev_ui.start()


# ═══════════════════════════════════════════════════════════════════════════
# CLI Entry Point
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="PM Copilot — AI Project Manager Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py --console     Interactive terminal mode
  python app.py --server      Start Bot Framework webhook server
  python app.py --devui       Launch MAF Developer UI
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--console", action="store_true",
        help="Run in interactive console mode",
    )
    group.add_argument(
        "--server", action="store_true",
        help="Start the MS Teams Bot webhook server",
    )
    group.add_argument(
        "--devui", action="store_true",
        help="Launch MAF Developer UI for visual debugging",
    )

    args = parser.parse_args()

    if args.console:
        asyncio.run(run_console())
    elif args.server:
        asyncio.run(run_server())
    elif args.devui:
        asyncio.run(run_devui())


if __name__ == "__main__":
    main()
