# 02-10 — Streaming, Chat Clients & Dev UI

> **Source**: Various samples in [02-agents/](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents) including `chat_client/`, `devui/`, and provider-specific streaming examples
> **Difficulty**: Beginner–Intermediate
> **Prerequisites**: [01 — Get Started](01-get-started.md)

## Overview

This guide covers three remaining agent capabilities: **response streaming** for real-time output, **chat clients** for structured interaction, and **Dev UI** for browser-based agent testing.

---

## 1. Response Streaming

Stream agent responses token-by-token instead of waiting for the full response.

### Basic Streaming
```python
# Non-streaming: wait for complete response
result = await agent.run("Tell me a story")
print(result.text)

# Streaming: get tokens as they arrive
async for chunk in agent.run("Tell me a story", stream=True):
    if chunk.text:
        print(chunk.text, end="", flush=True)
```

### Streaming with Tool Calls
When streaming, tool calls are executed inline. You can observe both text tokens and tool activity:

```python
async for chunk in agent.run("What's the weather?", stream=True):
    if chunk.text:
        print(chunk.text, end="")
    if chunk.user_input_requests:
        # Handle approval requests during streaming
        pass
```

### Background Responses
Some providers support background execution where the model processes requests asynchronously:

```python
result = await agent.run("Process this data", options={"store": True})
# Result includes response_id for later retrieval
```

---

## 2. Chat Clients

Chat clients provide direct access to the underlying model without the full agent abstraction.

### Built-in Chat Clients
```python
from agent_framework.openai import OpenAIChatClient

# Use as a direct chat client
client = OpenAIChatClient()
response = await client.get_response(
    messages=[Message("user", "Hello!")],
    instructions="You are helpful.",
)
print(response.text)
```

### Custom Chat Client
Subclass `BaseChatClient` to create your own model integration:

```python
from agent_framework import BaseChatClient

class MyChatClient(BaseChatClient):
    async def get_response(self, messages, instructions=None, **kwargs):
        # Your custom model integration
        ...
```

### Chat Client → Agent
Every chat client can become an agent:
```python
agent = OpenAIChatClient().as_agent(
    name="MyAgent", instructions="...", tools=[...]
)
```

---

## 3. Dev UI

MAF includes a **browser-based development UI** for testing agents interactively.

### Available Dev UI Samples

| Sample | What It Shows |
|--------|--------------|
| `devui/weather_agent_azure/` | Weather agent with Azure backend |
| `devui/foundry_agent/` | Azure AI Foundry agent |
| `devui/declarative/` | Declarative agent testing |
| `devui/workflow_agents/` | Workflow agent testing |
| `devui/fanout_workflow/` | Fan-out workflow visualization |
| `devui/spam_workflow/` | Spam detection workflow |
| `devui/in_memory_mode.py` | Fully local testing |

### Running Dev UI
```bash
# Typically:
python -m agent_framework.devui.app
# or via the specific sample script
```

---

## Typed Agent Options

Pass provider-specific options through the `options` parameter:

```python
result = await agent.run("question", options={
    "store": True,           # Enable server-side storage
    "temperature": 0.7,      # Model temperature
    "response_format": MyModel,  # Structured output
})
```

---

## 🎯 Key Takeaways

1. **`stream=True`** — Add to any `agent.run()` call for token-by-token output
2. **Chat clients ≠ agents** — Clients give raw model access; agents add tools, memory, middleware
3. **`.as_agent()`** — Upgrade any chat client to a full agent
4. **Dev UI** — Browser-based testing included out of the box
5. **Options dict** — Pass provider-specific settings without changing agent code

## What's Next

This concludes the **Agent Deep-Dive** section! Continue to:

→ [03-01 — Workflow Start Here](03-01-start-here.md) for workflow fundamentals
→ [03 — Workflow Patterns](README.md) for the full workflow guide index
