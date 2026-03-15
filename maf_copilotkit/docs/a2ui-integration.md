# A2UI + AG-UI Integration Guide

## What is A2UI?

**A2UI (Agent-to-UI)** is a declarative, LLM-friendly specification for generative UI. Instead of having the backend return raw data that the frontend must interpret, A2UI lets the agent return **UI declarations** (JSON-based component trees) that the frontend renders directly.

This means the agent controls _what_ gets displayed, while the frontend controls _how_ it looks.

## How A2UI Works with AG-UI

AG-UI is the transport protocol (SSE events). A2UI rides on top of AG-UI via **custom events**:

```
Agent  →  AG-UI SSE custom event (type: "a2ui")  →  CopilotKit  →  Render A2UI component
```

### Event Flow

1. MAF agent calls a tool that generates an A2UI payload
2. The AG-UI endpoint emits a custom event with the A2UI JSON
3. CopilotKit's A2UI middleware intercepts the event
4. The middleware maps A2UI component declarations to React components
5. The UI renders the declared layout

## Enabling A2UI in CopilotKit

### 1. Install the middleware

```bash
pnpm add @ag-ui/a2ui-middleware
```

### 2. Register A2UI components

```tsx
// In your CopilotKit provider setup
import { A2UIProvider } from "@ag-ui/a2ui-middleware";

<CopilotKit runtimeUrl={agentUrl}>
  <A2UIProvider
    components={{
      // Map A2UI component names to React components
      "TaskCard": TaskCard,
      "EventList": EventList,
      "StatusBadge": StatusBadge,
    }}
  >
    {children}
  </A2UIProvider>
</CopilotKit>
```

### 3. Backend: Return A2UI payloads from tools

```python
# In your MAF tool, return an A2UI-compatible response
def get_tasks():
    return {
        "a2ui": {
            "component": "TaskCard",
            "props": {
                "tasks": [
                    {"title": "Design system", "status": "In Progress"}
                ]
            }
        }
    }
```

## Migration Path

The current starter uses `useRenderTool` to map tool names to React components. To migrate to A2UI:

1. **Keep existing tool renderers** as fallbacks
2. **Add A2UI middleware** alongside CopilotKit
3. **Update tools** to return A2UI payloads when the frontend supports it
4. **Gradually remove** `useRenderTool` hooks as A2UI coverage increases

A2UI and `useRenderTool` can coexist — A2UI takes precedence when an A2UI payload is present.

## References

- [CopilotKit A2UI docs](https://docs.copilotkit.ai/microsoft-agent-framework/generative-ui/a2ui)
- [AG-UI Protocol](https://docs.ag-ui.com/introduction)
- [A2UI Specification](https://github.com/nichochar/a2ui)
