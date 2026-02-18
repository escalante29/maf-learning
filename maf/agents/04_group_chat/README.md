# Pattern 04 — Group Chat: Sprint Planning Debate

## What Is the Group Chat Pattern?

The **Group Chat** pattern models a **collaborative conversation** among multiple agents, coordinated by a central orchestrator that decides who speaks next. Unlike Handoff (where agents decide routing), the orchestrator controls the flow.

```
Input → Orchestrator → Agent A → Orchestrator → Agent B → Orchestrator → Agent C → ...
                           ↑___________________________|
                           (full conversation shared)
```

**Key properties:**
- **Centralized coordination**: an orchestrator picks the next speaker (round-robin, prompt-based, or custom logic)
- **Shared context**: all agents see the full conversation history — they can build on or challenge each other
- **Iterative refinement**: agents can go through multiple rounds, refining the output collaboratively
- **Flexible termination**: the orchestrator or a termination condition ends the conversation
- **Star topology** internally: orchestrator ↔ all agents

## This Example: Sprint Planning Debate

Three agents debate and refine a backlog prioritisation, coordinated by a round-robin orchestrator. Each agent has a distinct role and perspective.

```
User: "Plan sprint 43 backlog: [5 stories]"
        ↓
  Round 1:
    product_owner_agent  → advocates for user value and business priority
    tech_lead_agent      → challenges complexity, flags dependencies
    scrum_master_agent   → facilitates, checks capacity, calls for consensus
  Round 2:
    product_owner_agent  → responds to tech lead's concerns
    tech_lead_agent      → refines estimates after PO clarification
    scrum_master_agent   → synthesises agreement, proposes final backlog
        ↓
  Output: agreed sprint backlog with rationale
```

### Why Group Chat here?
The **iterative debate** between agents — where each response influences the next — is exactly what Group Chat is designed for. The PO and Tech Lead need to hear each other's arguments and respond. Round-robin ensures both get equal voice, and the Scrum Master acts as a natural terminator.

## How to Run

```bash
cd maf
source .venv/bin/activate
python -m agents.04_group_chat.workflow
```

## When to Use Group Chat

✅ Agents need to **debate, critique, and refine** each other's work  
✅ You want **multi-perspective analysis** with iterative rounds  
✅ You need a **collaborative problem-solving** session  
✅ You want **flexible speaker selection** (round-robin, LLM-based, or custom)  

❌ Avoid if agents are independent (use Concurrent — it's faster)  
❌ Avoid if each step strictly depends on the prior (use Sequential)  
❌ Avoid if you need user-driven routing (use Handoff)  

## Group Chat vs. Handoff

| | Group Chat | Handoff |
|---|---|---|
| **Who picks next speaker?** | Central orchestrator | The current agent (via tool call) |
| **Conversation style** | Debate / refinement | Triage / routing |
| **Shared history?** | ✅ Yes | ✅ Yes |
| **User in the loop?** | Optional | ✅ Yes (between hops) |

## MAF API

```python
from agent_framework.orchestrations import GroupChatBuilder

workflow = (
    GroupChatBuilder(participants=[agent_a, agent_b, agent_c])
    .with_max_rounds(3)
    .build()
)

events = await workflow.run("Your input prompt")
```

## Further Reading

- [MS Learn — Group Chat Orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/group-chat/)
