# Combining MAF Handoff + Concurrent Patterns

> **Context:** This document is based on reading the `agent_framework_orchestrations` package source code installed in `maf/.venv`, and the existing PM Copilot codebase in `maf/`.

---

## How Each Pattern Works Internally

### Handoff Pattern

The `HandoffBuilder` creates a **decentralized, conversational** workflow:

```
User Input → Start Agent → [Agent A calls handoff_to_B tool] → Agent B → [calls handoff_to_A] → Agent A → ... → User
```

**Key mechanics (from `_handoff.py`):**
- Each agent gets synthetic `handoff_to_<target>` tools injected by `_AutoHandoffMiddleware`
- When an LLM calls a handoff tool, the middleware **short-circuits** execution and routes the full conversation to the target agent
- All agents share the **full conversation history** (broadcast via `_broadcast_messages`)
- The workflow pauses and emits a `request_info` event when an agent responds *without* triggering a handoff — this is when the user gets to reply
- Termination: a `termination_condition` lambda checks the conversation, or the user sends an empty response

**Topology:** Star (our code), Mesh (default if no `.add_handoff()` calls), or any custom DAG.

---

### Concurrent Pattern

The `ConcurrentBuilder` creates a **parallel fan-out/fan-in** workflow:

```
Input → Dispatcher → [Agent A | Agent B | Agent C] (parallel) → Aggregator → Output
```

**Key mechanics (from `_concurrent.py`):**
- `_DispatchToAllParticipants`: broadcasts the input to all participants simultaneously
- Each participant runs independently and in parallel (no shared conversation)
- `_AggregateAgentConversations` (default): collects all `AgentExecutorResponse` objects and combines them into a `list[Message]` — one user prompt + one final assistant message per agent
- Custom aggregator: override with `.with_aggregator(callback_or_executor)` to merge results any way you want
- `with_request_info()`: enables human-in-the-loop (HIL) — the workflow pauses after each parallel agent finishes, before aggregation

**Key difference from Handoff:** Concurrent is **single-shot** (one input → one aggregated output). Handoff is **conversational** (multi-turn, user stays in the loop between turns).

---

## Three Strategies to Combine Them

### Strategy 1: Concurrent *inside* Handoff (Recommended for PM Copilot)

**Use case:** The triage agent routes to a specialist, and that specialist fans out to multiple sub-agents in parallel to gather data, then synthesizes the result.

**Example:** The `meetings_agent` is handed off to, and it concurrently runs `transcript_fetcher`, `attendee_fetcher`, and `task_extractor` agents in parallel, then synthesizes the result before handing back to triage.

```
User → Triage → meetings_agent (Handoff hop)
                    ↓
              ConcurrentBuilder workflow
              ┌──────────────────────────────┐
              │  transcript_fetcher_agent    │
              │  attendee_fetcher_agent      │ (parallel)
              │  task_extractor_agent        │
              └──────────────────────────────┘
                    ↓ aggregated result
              meetings_agent synthesizes → hands back to Triage
```

**Implementation approach:**

The specialist agent's tool calls a sub-workflow internally. The specialist agent itself stays in the Handoff workflow; the concurrent execution is hidden inside a tool.

```python
# tools/meetings_tools.py — wrap concurrent sub-workflow in a tool
from agent_framework.orchestrations import ConcurrentBuilder
from agent_framework import tool

@tool(approval_mode="never_require")
async def analyze_meeting_comprehensive(meeting_id: str) -> str:
    """Run transcript, attendee, and task extraction concurrently for a meeting."""
    client = OpenAIChatClient(api_key=settings.openai_api_key)

    transcript_agent = Agent(client=client, name="transcript_agent",
                             instructions="Fetch and summarize the meeting transcript.")
    attendee_agent   = Agent(client=client, name="attendee_agent",
                             instructions="List attendees and their roles.")
    tasks_agent      = Agent(client=client, name="tasks_agent",
                             instructions="Extract action items from the transcript.")

    concurrent_wf = (
        ConcurrentBuilder(participants=[transcript_agent, attendee_agent, tasks_agent])
        .with_aggregator(lambda results: json.dumps({
            "transcript": results[0].agent_response.messages[-1].text,
            "attendees":  results[1].agent_response.messages[-1].text,
            "tasks":      results[2].agent_response.messages[-1].text,
        }))
        .build()
    )

    events = await concurrent_wf.run(f"Analyze meeting ID: {meeting_id}")
    # Extract the output event
    for event in events:
        if event.type == "output":
            return event.data  # The JSON string from the aggregator
    return "{}"
```

The `meetings_agent` in the Handoff workflow calls this tool normally — the concurrent execution is completely transparent to the Handoff orchestrator.

---

### Strategy 2: Handoff *inside* Concurrent (Fan-out with specialist routing)

**Use case:** You want to fan out the same user query to multiple independent Handoff sub-workflows (e.g., one for SharePoint, one for Meetings), run them in parallel, then aggregate their answers.

```
User Input
    ↓
ConcurrentBuilder (outer)
┌─────────────────────────────────────────────────┐
│  HandoffWorkflow A (SharePoint triage + agents) │
│  HandoffWorkflow B (Meetings triage + agents)   │ (parallel)
└─────────────────────────────────────────────────┘
    ↓ aggregated
Final synthesized answer
```

**Implementation approach:**

Wrap each Handoff workflow as an `Executor` participant in the `ConcurrentBuilder`. This requires creating a custom `Executor` subclass that runs a Handoff workflow internally.

```python
from agent_framework._workflows._executor import Executor, handler
from agent_framework._workflows._workflow_context import WorkflowContext
from agent_framework._workflows._agent_executor import AgentExecutorResponse

class HandoffSubWorkflowExecutor(Executor):
    """Wraps a HandoffBuilder workflow as a ConcurrentBuilder participant."""

    def __init__(self, workflow, executor_id: str):
        super().__init__(id=executor_id)
        self._workflow = workflow

    @handler
    async def run(self, prompt: str, ctx: WorkflowContext) -> None:
        events = await self._workflow.run(prompt)
        # Find the final output from the handoff workflow
        output_text = ""
        for event in events:
            if event.type == "output" and isinstance(event.data, list):
                # list[Message] — the final conversation
                output_text = event.data[-1].text if event.data else ""
        # Yield as AgentExecutorResponse for the aggregator
        from agent_framework import AgentResponse, Message
        response = AgentResponse(messages=[Message(role="assistant", text=output_text)])
        await ctx.yield_output(AgentExecutorResponse(agent_response=response))
```

> [!WARNING]
> This approach is complex. The inner Handoff workflows are **conversational** (multi-turn), but `ConcurrentBuilder` is **single-shot**. You'd need to run the Handoff workflow in autonomous mode (`.with_autonomous_mode()`) or pre-terminate it after one turn, otherwise the concurrent workflow will hang waiting for user input from the inner handoff.

---

### Strategy 3: Hybrid — Triage Handoff → Concurrent Specialist Group

**Use case:** The triage agent routes to a "concurrent coordinator" specialist, which fans out to multiple sub-agents and synthesizes a combined answer. This is the cleanest architecture for PM Copilot.

```
User → Triage (Handoff)
         ↓ handoff_to_research_coordinator
       ResearchCoordinator (Handoff participant, no tools)
         ↓ calls internal concurrent workflow via tool
       [Agent A | Agent B | Agent C] (ConcurrentBuilder)
         ↓ aggregated JSON
       ResearchCoordinator synthesizes → hands back to Triage
         ↓
       Triage → User
```

This is essentially Strategy 1 but with a dedicated "coordinator" agent in the Handoff graph whose sole job is to orchestrate concurrent sub-agents.

---

## Event Handling Differences

| Aspect | Handoff | Concurrent |
|---|---|---|
| **Output event** | `AgentResponse` (per agent turn) | `list[Message]` (aggregated, one shot) |
| **User input events** | `request_info` with `HandoffAgentUserRequest` | `request_info` only if `.with_request_info()` enabled |
| **Handoff events** | `handoff_sent` with `source`/`target` | None |
| **Termination** | `termination_condition` lambda or empty user response | Automatic after aggregation |
| **Multi-turn** | ✅ Yes (conversational) | ❌ No (single-shot by default) |

When combining (Strategy 1), the outer Handoff workflow's event loop in `app.py` remains unchanged — the concurrent sub-workflow runs and completes entirely inside a tool call, so no new event types are exposed to the outer loop.

---

## Aggregation Strategies for Concurrent

When using `ConcurrentBuilder` inside a tool (Strategy 1), choose your aggregator based on what the specialist agent needs:

```python
# Option A: Return structured JSON (easiest for the LLM to parse)
.with_aggregator(lambda results: json.dumps({
    agent_name: results[i].agent_response.messages[-1].text
    for i, agent_name in enumerate(["transcript", "attendees", "tasks"])
}))

# Option B: Return concatenated text
.with_aggregator(lambda results: "\n\n---\n\n".join(
    r.agent_response.messages[-1].text for r in results
))

# Option C: Custom async aggregator with synthesis agent
async def synthesize(results, ctx):
    combined = "\n".join(r.agent_response.messages[-1].text for r in results)
    synthesis_agent = Agent(client=client, name="synthesizer", instructions="Synthesize these reports.")
    response = await synthesis_agent.run(combined)
    await ctx.yield_output(response.messages[-1].text)

.with_aggregator(synthesize)
```

---

## Key Design Considerations

1. **Conversation history isolation:** Concurrent sub-agents do NOT share conversation history with the outer Handoff workflow. If the sub-agents need context (e.g., the meeting ID), pass it explicitly in the prompt string to `concurrent_wf.run(prompt)`.

2. **Autonomous mode for inner Handoff:** If you embed a Handoff workflow inside Concurrent (Strategy 2), enable `.with_autonomous_mode()` on the inner `HandoffBuilder` to prevent it from pausing for user input mid-concurrent-run.

3. **Shared LLM client:** All agents (inner and outer) can share the same `OpenAIChatClient` instance — it's thread-safe and connection-pooled.

4. **Error handling:** The default `_AggregateAgentConversations` raises `RuntimeError` if no assistant replies are found. Wrap the concurrent tool call in a try/except in your specialist agent's tool.

5. **Intermediate outputs:** Set `intermediate_outputs=True` on `ConcurrentBuilder` if you want to stream partial results from each parallel agent before aggregation.

---

## Recommended Next Step for PM Copilot

The cleanest path is **Strategy 1**: wrap a `ConcurrentBuilder` workflow inside a `@tool`-decorated async function in the relevant `tools/*.py` module. This requires:

1. Create a new tool (e.g., `analyze_meeting_comprehensive` in `meetings_tools.py`)
2. Inside the tool, build and run a `ConcurrentBuilder` workflow
3. Return the aggregated JSON string
4. Add the new tool to the relevant agent's `tools=[...]` list in `agents/meetings_agent.py`
5. No changes needed to `handoff_workflow.py` or `app.py`
