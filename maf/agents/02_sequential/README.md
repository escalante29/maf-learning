# Pattern 02 — Sequential: Sprint Report Pipeline

## What Is the Sequential Pattern?

The **Sequential** pattern runs agents in a **pipeline** — one after another. Each agent receives the full conversation history from all prior agents, so every step builds on the previous.

```
Input → Agent A → Agent B → Agent C → Output
         (raw)   (analysis)  (report)
```

**Key properties:**
- Strictly ordered — Agent B cannot start until Agent A finishes
- Full conversation history is passed forward at each step
- Output of the last agent is the workflow's final output
- No user interaction between steps (single-shot)

## This Example: Sprint Report Pipeline

A 3-stage pipeline that transforms raw sprint data into a polished executive report.

```
User: "Generate sprint report for Sprint 42"
        ↓
  data_collector_agent   → gathers raw sprint data (velocity, stories, blockers)
        ↓
  analyst_agent          → structures the data: completed vs. incomplete, trends
        ↓
  writer_agent           → writes a polished markdown executive report
        ↓
  Output: final sprint report
```

### Why Sequential here?
Each stage **strictly depends** on the previous one's output. The analyst can't structure data that hasn't been collected; the writer can't write a report without the analysis. There's no benefit to parallelism.

## How to Run

```bash
cd maf
source .venv/bin/activate
python -m agents.02_sequential.workflow
```

## When to Use Sequential

✅ Each step **depends on** the previous step's output  
✅ You want a **document processing pipeline** (collect → analyse → write)  
✅ You need **multi-stage reasoning** where each agent refines the prior result  
✅ Order matters and parallelism would produce incorrect results  

❌ Avoid if steps are independent (use Concurrent instead — it's faster)  
❌ Avoid if you need agents to debate or refine each other's work (use Group Chat)  

## MAF API

```python
from agent_framework.orchestrations import SequentialBuilder

workflow = SequentialBuilder(participants=[agent_a, agent_b, agent_c]).build()

events = await workflow.run("Your input prompt")
```

## Further Reading

- [MS Learn — Sequential Orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/sequential/)
