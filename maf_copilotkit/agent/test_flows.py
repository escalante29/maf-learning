"""
End-to-end AG-UI flow tester.
Sends realistic multi-turn conversations directly to the backend and prints
a structured summary of every event received, highlighting any errors.
"""

from __future__ import annotations

import asyncio
import json
import sys
import uuid
from dataclasses import dataclass, field
from typing import Any

import httpx

ENDPOINT = "http://localhost:8000/copilotkit"
THREAD_TIMEOUT = 120  # seconds per request


@dataclass
class RunResult:
    scenario: str
    turn: int
    events: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    tool_calls: list[str] = field(default_factory=list)
    tool_results: list[str] = field(default_factory=list)
    state_snapshots: list[dict] = field(default_factory=list)
    has_run_finished: bool = False
    has_run_error: bool = False

    @property
    def ok(self) -> bool:
        return self.has_run_finished and not self.has_run_error and not self.errors


def _ag_ui_payload(messages: list[dict], thread_id: str, run_id: str) -> dict:
    return {
        "thread_id": thread_id,
        "run_id": run_id,
        "agent_name": "default",
        "messages": messages,
        "forwarded_props": {},
    }


async def run_single_turn(
    scenario: str,
    turn: int,
    messages: list[dict],
    thread_id: str,
) -> tuple[RunResult, list[dict]]:
    """Stream one AG-UI turn; returns (result, updated_message_list)."""
    run_id = str(uuid.uuid4())
    result = RunResult(scenario=scenario, turn=turn)
    payload = _ag_ui_payload(messages, thread_id, run_id)

    assistant_msgs: list[dict] = []
    open_tool_calls: dict[str, str] = {}  # id → name
    # tool results keyed by toolCallId — appended after stream in proper order
    tool_results: dict[str, dict] = {}
    resulted_calls: set[str] = set()  # calls that received TOOL_CALL_RESULT
    current_text_msg: dict | None = None

    try:
        async with httpx.AsyncClient(timeout=THREAD_TIMEOUT) as client:
            async with client.stream(
                "POST",
                ENDPOINT,
                json=payload,
                headers={"Accept": "text/event-stream", "Content-Type": "application/json"},
            ) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    result.errors.append(f"HTTP {resp.status_code}: {body[:200]}")
                    return result, messages

                async for raw_line in resp.aiter_lines():
                    if not raw_line.startswith("data:"):
                        continue
                    data_str = raw_line[5:].strip()
                    if not data_str or data_str == "[DONE]":
                        continue
                    try:
                        event = json.loads(data_str)
                    except json.JSONDecodeError:
                        result.errors.append(f"Bad JSON: {data_str[:80]}")
                        continue

                    etype = event.get("type", "")
                    result.events.append(etype)

                    if etype == "RUN_STARTED":
                        pass

                    elif etype == "TOOL_CALL_START":
                        tid = event.get("toolCallId") or event.get("tool_call_id", "")
                        tname = event.get("toolCallName") or event.get("tool_call_name", "")
                        open_tool_calls[tid] = tname
                        result.tool_calls.append(tname)
                        # Start a new assistant message if:
                        # - there is no previous message
                        # - the last message is a text/content message (has content)
                        # - any existing tool call in the last message has already received
                        #   a result (→ this is a new sequential MAF agent turn, not a
                        #   parallel multi-tool call within the same turn)
                        last = assistant_msgs[-1] if assistant_msgs else None
                        last_tcs = last.get("toolCalls", []) if last else []
                        prev_turn_complete = any(
                            tc["id"] in resulted_calls for tc in last_tcs
                        )
                        if (
                            last is None
                            or last.get("role") != "assistant"
                            or last.get("content")
                            or prev_turn_complete
                        ):
                            last = {
                                "id": str(uuid.uuid4()),
                                "role": "assistant",
                                "content": "",
                                "toolCalls": [],
                            }
                            assistant_msgs.append(last)
                        last.setdefault("toolCalls", []).append({
                            "id": tid,
                            "type": "function",
                            "function": {"name": tname, "arguments": ""},
                        })

                    elif etype == "TOOL_CALL_ARGS_DELTA":
                        tid = event.get("toolCallId") or event.get("tool_call_id", "")
                        delta = event.get("delta", "")
                        for msg in reversed(assistant_msgs):
                            if msg.get("role") == "assistant":
                                for tc in msg.get("toolCalls", []):
                                    if tc["id"] == tid:
                                        tc["function"]["arguments"] += delta
                                        break
                                break

                    elif etype == "TOOL_CALL_END":
                        tid = event.get("toolCallId") or event.get("tool_call_id", "")
                        open_tool_calls.pop(tid, None)

                    elif etype == "TOOL_CALL_RESULT":
                        tid = event.get("toolCallId") or event.get("tool_call_id", "")
                        content = event.get("content", "")
                        result.tool_results.append(f"{tid[:8]}…: {content[:60]}")
                        # Collect but do NOT append yet — ordering is fixed after the stream.
                        tool_results[tid] = {
                            "id": event.get("messageId") or str(uuid.uuid4()),
                            "role": "tool",
                            "toolCallId": tid,
                            "content": content,
                        }
                        resulted_calls.add(tid)

                    elif etype == "TEXT_MESSAGE_START":
                        mid = event.get("messageId") or event.get("message_id", str(uuid.uuid4()))
                        current_text_msg = {"id": mid, "role": "assistant", "content": ""}
                        assistant_msgs.append(current_text_msg)

                    elif etype == "TEXT_MESSAGE_CONTENT":
                        if current_text_msg is not None:
                            current_text_msg["content"] += event.get("delta", "")

                    elif etype == "TEXT_MESSAGE_END":
                        current_text_msg = None

                    elif etype == "STATE_SNAPSHOT":
                        snap = event.get("snapshot", {})
                        if snap:
                            result.state_snapshots.append(snap)

                    elif etype == "RUN_FINISHED":
                        result.has_run_finished = True

                    elif etype == "RUN_ERROR":
                        result.has_run_error = True
                        result.errors.append(f"RUN_ERROR: {event.get('message', '?')}")

    except Exception as exc:
        result.errors.append(f"Exception: {exc}")

    # Rebuild history in correct OpenAI order:
    #   assistant message (with toolCalls) → tool results for those calls → …
    # This avoids the "tool message must follow tool_calls" 400 error on turn 2+.
    for msg in assistant_msgs:
        if msg in messages:
            continue
        messages.append(msg)
        # Immediately follow with tool results for every tool call in this message.
        for tc in msg.get("toolCalls", []):
            tr = tool_results.pop(tc["id"], None)
            if tr is not None:
                messages.append(tr)

    # Any leftover tool results (shouldn't happen, but be safe).
    for tr in tool_results.values():
        messages.append(tr)

    return result, messages


async def run_scenario(
    scenario: str,
    turns: list[str],
) -> list[RunResult]:
    thread_id = str(uuid.uuid4())
    messages: list[dict] = []
    results: list[RunResult] = []

    for i, user_text in enumerate(turns, 1):
        messages.append({"id": str(uuid.uuid4()), "role": "user", "content": user_text})
        result, messages = await run_single_turn(scenario, i, list(messages), thread_id)
        results.append(result)

    return results


SCENARIOS: list[tuple[str, list[str]]] = [
    ("single_get_tasks",        ["Show me my tasks"]),
    ("single_calendar",         ["What meetings do I have this week?"]),
    ("single_search_docs",      ["Search for documents about the API"]),
    ("single_create_meeting",   ["Schedule a standup for tomorrow 2026-03-15 at 9am, duration 30 minutes, attendees alice@example.com bob@example.com"]),
    ("multi_tasks_then_docs",   ["What tasks are overdue and do we have any related documents?"]),
    ("multi_tasks_then_calendar", ["Show me my tasks and schedule a standup for 2026-03-18 at 9am with alice@example.com and bob@example.com"]),
    ("multi_turn_t1",           ["Show me my tasks"]),
    ("multi_turn_t2",           ["Show me my tasks", "Now show me my calendar events for the next week"]),
    ("multi_turn_t3",           ["What tasks are overdue and do we have any related documents?", "Schedule a standup for 2026-03-20 at 10am with the whole team"]),
]


def print_result(r: RunResult) -> None:
    status = "✅ PASS" if r.ok else "❌ FAIL"
    print(f"  Turn {r.turn}: {status}")
    print(f"    Events      : {', '.join(r.events) or '(none)'}")
    if r.tool_calls:
        print(f"    Tool calls  : {', '.join(r.tool_calls)}")
    if r.tool_results:
        print(f"    Tool results: {len(r.tool_results)} received")
    if r.state_snapshots:
        titles = [s.get('title', '?') for s in r.state_snapshots if s.get('title')]
        print(f"    State titles: {titles}")
    if r.errors:
        for e in r.errors:
            print(f"    ⚠  ERROR: {e}")


async def main() -> int:
    all_ok = True
    for scenario, turns in SCENARIOS:
        print(f"\n{'─'*60}")
        print(f"Scenario: {scenario}")
        results = await run_scenario(scenario, turns)
        for r in results:
            print_result(r)
            if not r.ok:
                all_ok = False

    print(f"\n{'═'*60}")
    print("ALL PASS ✅" if all_ok else "SOME FAILURES ❌")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
