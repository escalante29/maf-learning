# Pattern 01 — Handoff: PM Triage Copilot

## What Is the Handoff Pattern?

The **Handoff** pattern is a **decentralized, conversational** multi-agent workflow. Agents route control to each other by calling synthetic `handoff_to_<agent>` tools that MAF injects automatically. There is no central orchestrator — each agent decides where to go next.

```
User Input → Start Agent → [Agent A calls handoff_to_B] → Agent B → [calls handoff_to_A] → ...
```

**Key properties:**
- All agents share the **full conversation history** on every hop
- The workflow pauses for user input whenever an agent responds *without* triggering a handoff
- Topology can be Star, Mesh, or any custom DAG via `.add_handoff()`
- Termination is controlled by a `termination_condition` lambda or an empty user response

## This Project's Implementation

This is the **existing** PM Copilot implementation. See:

| File | Role |
|---|---|
| [`maf/orchestration/handoff_workflow.py`](../../orchestration/handoff_workflow.py) | Wires all 6 agents into a star topology via `HandoffBuilder` |
| [`maf/agents/triage.py`](../triage.py) | Coordinator — routes to specialists, never does specialist work |
| [`maf/agents/sharepoint_agent.py`](../sharepoint_agent.py) | SharePoint CRUD specialist |
| [`maf/agents/meetings_agent.py`](../meetings_agent.py) | Meeting transcripts + AI analysis |
| [`maf/agents/calendar_agent.py`](../calendar_agent.py) | Scheduling and calendar events |
| [`maf/agents/documents_agent.py`](../documents_agent.py) | XLSX / PPTX generation |
| [`maf/agents/project_info_agent.py`](../project_info_agent.py) | General PM knowledge (no tools) |

## Routing Topology

```
                    ┌─────────────────┐
                    │  triage_agent   │  ← Start agent
                    └────────┬────────┘
          ┌─────────┬────────┼────────┬──────────┐
          ↓         ↓        ↓        ↓          ↓
     sharepoint  meetings calendar documents project_info
          │         │        │        │          │
          └─────────┴────────┴────────┴──────────┘
                             │
                    back to triage_agent
```

## How to Run

```bash
cd maf
python app.py --console
# or
python app.py --devui
```

## When to Use Handoff

✅ You have a **triage-and-route** pattern (one coordinator, many specialists)  
✅ The conversation is **multi-turn** and the user stays in the loop  
✅ Each specialist has **distinct tools** and expertise  
✅ You want **decentralized routing** — agents decide where to go, not a central orchestrator  

❌ Avoid if all agents need to run simultaneously (use Concurrent)  
❌ Avoid if you need iterative refinement between agents (use Group Chat)  
❌ Avoid if the task path is completely unknown in advance (use Magentic)  

## MAF API

```python
from agent_framework.orchestrations import HandoffBuilder

workflow = (
    HandoffBuilder(
        name="my_workflow",
        participants=[triage, agent_a, agent_b],
        termination_condition=lambda conv: ...,
    )
    .with_start_agent(triage)
    .add_handoff(triage, [agent_a, agent_b])   # triage → specialists
    .add_handoff(agent_a, [triage])             # specialists → triage
    .add_handoff(agent_b, [triage])
    .build()
)
```

## Further Reading

- [MS Learn — Handoff Orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/handoff/)
- [`maf/docs/APPLICATION_FLOW.md`](../../docs/APPLICATION_FLOW.md) — deep dive into this project's Handoff implementation
- [`maf/docs/handoff_vs_concurrent_research.md`](../../docs/handoff_vs_concurrent_research.md) — combining Handoff with Concurrent
