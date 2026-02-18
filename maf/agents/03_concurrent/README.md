# Pattern 03 — Concurrent: Project Health Check

## What Is the Concurrent Pattern?

The **Concurrent** pattern fans out a single input to **all agents simultaneously**, then collects and aggregates their results. It's the fastest pattern when tasks are independent.

```
Input → Dispatcher → [Agent A | Agent B | Agent C | Agent D]  (parallel)
                              ↓
                         Aggregator → Output
```

**Key properties:**
- All agents run **at the same time** — total latency ≈ slowest single agent (not sum of all)
- Agents are **isolated** — they don't share conversation history with each other
- A default aggregator combines results into `list[Message]`; a custom aggregator can produce any output
- Single-shot: one input → one aggregated output (not conversational)
- `with_request_info()` enables human-in-the-loop review before aggregation

## This Example: Multi-Domain Project Health Check

When a PM asks for a full project health check, 4 independent specialist agents run in parallel, each analysing a different dimension of project health.

```
User: "Health check for Project Alpha"
        ↓
  ┌─────────────────────────────────────────────────────┐
  │  budget_agent    → burn rate vs. plan               │
  │  timeline_agent  → milestone completion vs. schedule │  (parallel)
  │  risk_agent      → open risks and blockers          │
  │  team_agent      → capacity and availability        │
  └─────────────────────────────────────────────────────┘
        ↓
  custom aggregator → combined JSON health dashboard
        ↓
  Output: structured health report
```

### Why Concurrent here?
All 4 checks are **completely independent** — budget data doesn't affect timeline data, etc. Running them in parallel cuts latency by ~75% compared to sequential.

## How to Run

```bash
cd maf
source .venv/bin/activate
python -m agents.03_concurrent.workflow
```

## When to Use Concurrent

✅ Tasks are **independent** of each other (no data dependencies between agents)  
✅ You need **fast results** — parallelism reduces total latency  
✅ You want **multiple perspectives** on the same input (ensemble reasoning)  
✅ You need a **fan-out/fan-in** pattern with a custom aggregation step  

❌ Avoid if Agent B needs Agent A's output (use Sequential)  
❌ Avoid if agents need to debate or refine each other's work (use Group Chat)  
❌ Avoid if routing depends on the user's intent (use Handoff)  

## MAF API

```python
from agent_framework.orchestrations import ConcurrentBuilder

workflow = (
    ConcurrentBuilder(participants=[agent_a, agent_b, agent_c])
    .with_aggregator(lambda results: " | ".join(
        r.agent_response.messages[-1].text for r in results
    ))
    .build()
)

events = await workflow.run("Your input prompt")
```

## Further Reading

- [MS Learn — Concurrent Orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/concurrent/)
- [`maf/docs/handoff_vs_concurrent_research.md`](../../docs/handoff_vs_concurrent_research.md) — combining Concurrent with Handoff
