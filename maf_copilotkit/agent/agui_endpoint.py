"""AG-UI endpoint — exposes the MAF HandoffBuilder workflow via the AG-UI protocol.

This module wraps the MAF workflow as an AG-UI-compatible agent and mounts
it on a FastAPI endpoint.  CopilotKit sends the full message history on
every turn, so we use `workflow_factory` to recreate the workflow for each
request (stateless).
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from ag_ui.core import BaseEvent, RunFinishedEvent, StateSnapshotEvent, ToolCallEndEvent, ToolCallResultEvent
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint
from agent_framework_ag_ui._workflow import AgentFrameworkWorkflow
import agent_framework_ag_ui._workflow_run as _wf_run
from orchestration.handoff_workflow import build_workflow

# ── Vendor bug workaround ─────────────────────────────────────────────────────
# _coerce_responses_for_pending_requests returns historical tool-result entries
# from the conversation history unchanged when there are no pending requests in
# the workflow.  run_workflow_stream then calls workflow.run(responses=…) which
# raises "No pending requests found in workflow context." on every turn after the
# first.  The correct behaviour when there are no pending requests is to return
# an empty dict so run_workflow_stream falls through to workflow.run(message=…).
_orig_coerce = _wf_run._coerce_responses_for_pending_requests


def _fixed_coerce_responses(
    responses: dict,
    pending_events: dict,
) -> dict:
    if not pending_events:
        return {}  # nothing to respond to — use message= path instead
    return _orig_coerce(responses, pending_events)


_wf_run._coerce_responses_for_pending_requests = _fixed_coerce_responses
# ─────────────────────────────────────────────────────────────────────────────

# Human-readable labels for each specialist tool: (card title, step label)
_TOOL_META: dict[str, tuple[str, str]] = {
    "get_tasks":            ("Fetching Tasks",       "Fetching project tasks"),
    "search_docs":          ("Searching Documents",  "Searching project documents"),
    "list_upcoming_events": ("Loading Calendar",     "Loading calendar events"),
    "create_meeting":       ("Creating Meeting",     "Creating calendar event"),
}

_COMPLETE    = "complete"
_IN_PROGRESS = "in_progress"
_PENDING     = "pending"

# Contextual follow-up suggestions shown in the chat input after each tool completes.
_TOOL_SUGGESTIONS: dict[str, list[dict[str, str]]] = {
    "get_tasks": [
        {"title": "Search documents", "message": "Search the project documents for related specs or notes"},
        {"title": "View my calendar",  "message": "Show my upcoming meetings this week"},
        {"title": "Filter by priority", "message": "Show me only high-priority tasks"},
    ],
    "search_docs": [
        {"title": "View current tasks",  "message": "Show me all current project tasks"},
        {"title": "Schedule a review",   "message": "Schedule a document review meeting for tomorrow at 2 PM"},
        {"title": "View my calendar",    "message": "Show my upcoming events for this week"},
    ],
    "list_upcoming_events": [
        {"title": "Schedule a meeting",  "message": "Create a new team meeting for next week"},
        {"title": "View project tasks",  "message": "Show me all current project tasks"},
        {"title": "Search documents",    "message": "Search for the latest project status reports"},
    ],
    "create_meeting": [
        {"title": "View my calendar",    "message": "Show my upcoming events for this week"},
        {"title": "View project tasks",  "message": "Show me all current project tasks"},
        {"title": "Search meeting notes","message": "Search for meeting notes or agendas"},
    ],
}


def _step(sid: str, label: str, status: str) -> dict[str, str]:
    return {"id": sid, "label": label, "status": status}


def _strip_tool_artifacts(messages: list[dict]) -> list[dict]:
    """Strip tool-call artifacts from the AG-UI message history.

    The HandoffBuilder calls clean_conversation_for_handoff internally which
    strips all function_call/function_result content anyway, then appends ALL
    historical function_result messages as runtime_tool_messages — creating
    orphaned role:"tool" entries without preceding tool_calls that OpenAI
    rejects with a 400 on multi-turn conversations.

    By pre-stripping these artifacts we hand the workflow only the text-based
    conversation history it actually needs for multi-turn routing.
    """
    result: list[dict] = []
    for msg in messages:
        role = msg.get("role", "")
        if role == "tool":
            continue  # drop all tool-result messages
        if role == "assistant":
            tool_calls = msg.get("toolCalls") or msg.get("tool_calls") or []
            content = msg.get("content") or ""
            if tool_calls and not content:
                continue  # drop pure tool-call assistant messages (no text)
            if tool_calls:
                # keep the text content but drop the toolCalls field
                result.append({k: v for k, v in msg.items() if k not in ("toolCalls", "tool_calls")})
                continue
        result.append(msg)
    return result


class _ToolCallFixer(AgentFrameworkWorkflow):
    """Wraps the workflow stream to inject missing TOOL_CALL_END and TOOL_CALL_RESULT events
    and to emit StateSnapshotEvent updates so the frontend can render a live progress card.

    run_workflow_stream converts AgentResponseUpdate objects to AG-UI events, but only
    processes assistant-role updates. Tool execution results (role="tool", type="function_result")
    are silently dropped as CustomEvent("workflow_output") and never become TOOL_CALL_RESULT
    events. Without TOOL_CALL_RESULT, the frontend's agent.messages never gains a role:"tool"
    entry, so useRenderTool renderers are permanently stuck in the "inProgress" state.

    Handoff tool calls also never receive TOOL_CALL_END, which causes @ag-ui/client's
    verifyEvents validator to reject RUN_FINISHED with 'Agent execution failed'.

    This wrapper:
    1. Strips tool-call artifacts from the incoming message history so the HandoffBuilder
       receives only the text conversation it needs for stateless multi-turn routing.
    2. Emits StateSnapshotEvent at each workflow phase so the frontend can show a live
       progress card (routing → executing → responding → done).
    3. Intercepts CustomEvent("workflow_output") events that carry function_result data and
       converts them into proper TOOL_CALL_END + TOOL_CALL_RESULT event pairs.
    4. Before RUN_FINISHED, closes any remaining open tool calls (handoffs) with synthetic
       TOOL_CALL_END + TOOL_CALL_RESULT events so the frontend marks them complete.
    """

    def _resolve_workflow(self, thread_id: str):  # type: ignore[override]
        """Always create a fresh workflow per request.

        CopilotKit is stateless — it resends the full message history on every
        turn.  The base-class implementation caches by thread_id, which means
        the second message reuses a HandoffBuilder instance that already ran to
        completion.  That stale instance raises an error when run() is called
        again, causing RUN_ERROR → stray CUSTOM events → client rejection.

        Creating a fresh workflow each request lets HandoffBuilder replay the
        entire history cleanly from an empty state.
        """
        if self._workflow_factory is None:
            raise NotImplementedError("workflow_factory is required")
        return self._workflow_factory(thread_id)

    async def run(self, input_data: dict[str, Any]) -> AsyncGenerator[BaseEvent]:
        # Pre-strip tool-call artifacts from the history before the workflow sees it.
        # HandoffBuilder.clean_conversation_for_handoff strips them internally anyway,
        # but keeping them causes orphaned role:"tool" entries that OpenAI rejects on
        # turn 2+ with a 400 "tool message must follow tool_calls" error.
        messages = input_data.get("messages")
        if messages:
            input_data = {**input_data, "messages": _strip_tool_artifacts(messages)}

        open_calls: set[str] = set()        # started, not yet TOOL_CALL_END
        pending_result: set[str] = set()    # started, not yet TOOL_CALL_RESULT
        tool_names: dict[str, str] = {}     # call_id → tool_name
        last_specialist_tool: str | None = None  # last _TOOL_META key invoked
        run_errored = False

        async for event in super().run(input_data):
            event_type = getattr(event, "type", "")

            # After a RUN_ERROR no further events are valid on the client side.
            # Swallow everything except the error itself (already yielded below).
            if run_errored:
                continue

            if event_type == "RUN_ERROR":
                run_errored = True
                # Clear the progress card so it doesn't stick on the UI.
                yield StateSnapshotEvent(snapshot={"suggestions": []})
                yield event
                continue

            if event_type == "TOOL_CALL_START":
                call_id = getattr(event, "tool_call_id", None)
                tool_name = getattr(event, "tool_call_name", "") or ""
                if call_id:
                    open_calls.add(call_id)
                    pending_result.add(call_id)
                    tool_names[call_id] = tool_name

                if tool_name in _TOOL_META:
                    last_specialist_tool = tool_name
                    # Specialist tool is about to execute — routing already done.
                    title, exec_label = _TOOL_META[tool_name]
                    yield StateSnapshotEvent(snapshot={
                        "title": title,
                        "steps": [
                            _step("route",   "Analyzing request",  _COMPLETE),
                            _step("execute", exec_label,           _IN_PROGRESS),
                            _step("respond", "Preparing response", _PENDING),
                        ],
                    })
                elif tool_name.startswith("handoff_to_") and "triage" not in tool_name:
                    # Triage is routing to a specialist — show routing phase.
                    yield StateSnapshotEvent(snapshot={
                        "title": "Processing Request",
                        "steps": [
                            _step("route",   "Analyzing request",  _IN_PROGRESS),
                            _step("execute", "Calling tool",       _PENDING),
                            _step("respond", "Preparing response", _PENDING),
                        ],
                    })

            elif event_type == "TOOL_CALL_END":
                call_id = getattr(event, "tool_call_id", None)
                if call_id:
                    open_calls.discard(call_id)

            elif event_type == "TOOL_CALL_RESULT":
                call_id = getattr(event, "tool_call_id", None)
                if call_id:
                    open_calls.discard(call_id)
                    pending_result.discard(call_id)

            elif event_type == "CUSTOM" and getattr(event, "name", None) == "workflow_output":
                # run_workflow_stream emits workflow_output CustomEvents for non-assistant-role
                # AgentResponseUpdate objects (i.e. function_result content from tool execution).
                # Convert these into proper TOOL_CALL_END + TOOL_CALL_RESULT pairs.
                value = getattr(event, "value", None)
                if isinstance(value, dict) and value.get("role") == "tool":
                    for content in value.get("contents", []):
                        if not isinstance(content, dict):
                            continue
                        if content.get("type") != "function_result":
                            continue
                        call_id = content.get("call_id")
                        if not call_id or call_id not in open_calls:
                            continue
                        result = content.get("result", "")
                        if not isinstance(result, str):
                            result = json.dumps(result)
                        tool_name = tool_names.get(call_id, "")

                        yield ToolCallEndEvent(tool_call_id=call_id)
                        yield ToolCallResultEvent(
                            message_id=str(uuid.uuid4()),
                            tool_call_id=call_id,
                            content=result,
                            role="tool",
                        )
                        open_calls.discard(call_id)
                        pending_result.discard(call_id)

                        # Advance to "responding" phase now that the tool returned data.
                        if tool_name in _TOOL_META:
                            title, exec_label = _TOOL_META[tool_name]
                            yield StateSnapshotEvent(snapshot={
                                "title": title,
                                "steps": [
                                    _step("route",   "Analyzing request",  _COMPLETE),
                                    _step("execute", exec_label,           _COMPLETE),
                                    _step("respond", "Preparing response", _IN_PROGRESS),
                                ],
                            })
                # Suppress the raw workflow_output event — it's internal noise.
                continue

            elif event_type == "RUN_FINISHED":
                # Close tool calls still open (handoff calls — no TOOL_CALL_END yet).
                for call_id in list(open_calls):
                    yield ToolCallEndEvent(tool_call_id=call_id)
                    yield ToolCallResultEvent(
                        message_id=str(uuid.uuid4()),
                        tool_call_id=call_id,
                        content="",
                        role="tool",
                    )
                    pending_result.discard(call_id)
                open_calls.clear()
                # Emit empty TOOL_CALL_RESULT for calls that had TOOL_CALL_END but no
                # result (e.g. request_info internal calls). Without this the frontend
                # keeps an unanswered assistant tool_calls entry in history, which
                # OpenAI rejects on the next turn with a 400 error.
                for call_id in list(pending_result):
                    yield ToolCallResultEvent(
                        message_id=str(uuid.uuid4()),
                        tool_call_id=call_id,
                        content="",
                        role="tool",
                    )
                pending_result.clear()
                # Clear the progress card and emit contextual follow-up suggestions.
                suggestions = _TOOL_SUGGESTIONS.get(last_specialist_tool or "", [])
                yield StateSnapshotEvent(snapshot={"suggestions": suggestions})

            yield event


def mount_agui_endpoint(app, path: str = "/copilotkit"):
    """Add the AG-UI endpoint to a FastAPI application.

    Uses `workflow_factory` so the AG-UI adapter creates a fresh workflow
    on every request — this matches CopilotKit's stateless model where the
    entire message history is sent on each turn.
    """
    wrapper = _ToolCallFixer(
        workflow_factory=build_workflow,
        name="default",
        description="PM Copilot — MAF + CopilotKit starter agent",
    )

    add_agent_framework_fastapi_endpoint(app, wrapper, path)

    @app.api_route(f"{path}/info", methods=["GET", "POST"])
    async def get_agui_info():
        """Expose info about the AG-UI agents.

        CopilotKit's CopilotRuntime expects agents to be an array and requires
        the endpoint to support POST.
        """
        return {
            "version": "1.0.0",
            "actions": [],
            "agents": [
                {
                    "name": "default",
                    "description": "PM Copilot — MAF + CopilotKit starter agent",
                }
            ],
        }
