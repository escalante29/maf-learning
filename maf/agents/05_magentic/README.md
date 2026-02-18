# Pattern 05 — Magentic: Autonomous Project Audit

## What Is the Magentic Pattern?

The **Magentic** pattern is the most powerful and autonomous MAF orchestration. A dedicated **Magentic manager** coordinates a pool of specialist agents, dynamically deciding which agent to invoke next based on the evolving context, task progress, and what information has been gathered so far.

```
Input → MagenticManager (plans + adapts) → Agent A → MagenticManager → Agent B → ...
                ↑_______________________________________________|
                (manager sees all results and re-plans)
```

**Key properties:**
- **Dynamic planning**: the manager creates and adapts a plan in real time — no fixed sequence
- **Adaptive delegation**: the manager may call the same agent multiple times, skip agents, or change order
- **Complex task handling**: designed for open-ended problems where the solution path is unknown in advance
- **Based on Magentic-One** (AutoGen): a research-backed multi-agent architecture
- **Python only** (not yet supported in C#)

> ⚠️ **Note:** The Magentic manager is a powerful LLM-based planner. It works best with GPT-4o or equivalent. Results may vary for simpler models.

## This Example: Autonomous Project Audit

A PM asks for a full end-to-end project audit. The Magentic manager dynamically plans which agents to call, in what order, and how many times — based on what it learns along the way.

```
User: "Audit Project Alpha end-to-end"
        ↓
  MagenticManager (plans):
    → document_reader_agent   (reads project docs and specs)
    → meeting_analyst_agent   (extracts decisions from transcripts)
    → risk_assessor_agent     (identifies risks from all gathered info)
    → report_writer_agent     (composes the final audit report)
        ↓
  Manager adapts: may re-run document_reader if gaps found,
                  may skip meeting_analyst if no transcripts exist
        ↓
  Output: comprehensive audit report
```

### Why Magentic here?
The audit path is **not known in advance**. The manager must reason about what information it has, what it still needs, and which agent can fill the gap. This is fundamentally different from Sequential (fixed order) or Group Chat (debate).

## How to Run

```bash
cd maf
source .venv/bin/activate
python -m agents.05_magentic.workflow
```

## When to Use Magentic

✅ The task is **complex and open-ended** — the solution path is unknown  
✅ You need **adaptive planning** — the workflow should change based on intermediate results  
✅ Agents may need to be called **multiple times** or in **varying order**  
✅ You want the most **autonomous** multi-agent behaviour  

❌ Avoid for simple tasks — the planning overhead is significant  
❌ Avoid if the sequence is known in advance (use Sequential — it's cheaper)  
❌ Avoid if you need deterministic, auditable execution paths  

## Magentic vs. Group Chat

| | Magentic | Group Chat |
|---|---|---|
| **Who picks next speaker?** | Powerful LLM planner (adaptive) | Orchestrator (round-robin or prompt) |
| **Planning** | ✅ Dynamic, multi-step planning | ❌ No explicit planning |
| **Task type** | Open-ended, complex | Collaborative refinement |
| **Predictability** | Lower (adaptive) | Higher (structured rounds) |
| **Cost** | Higher (manager LLM calls) | Lower |

## MAF API

```python
from agent_framework.orchestrations import MagenticBuilder

workflow = (
    MagenticBuilder(participants=[agent_a, agent_b, agent_c])
    .build()
)

events = await workflow.run("Your complex task prompt")
```

## Further Reading

- [MS Learn — Magentic Orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/magentic/)
- [Magentic-One paper (AutoGen)](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html)
