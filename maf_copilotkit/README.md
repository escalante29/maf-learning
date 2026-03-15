# MAF + CopilotKit Starter

Production-quality reference architecture for an **agentic application** running inside **Microsoft Teams**, powered by Microsoft Agent Framework, AG-UI, and CopilotKit.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Microsoft Teams Tab                                    │
│  ┌───────────────────────┐  ┌────────────────────────┐  │
│  │  Workspace Dashboard  │  │  CopilotKit Sidebar    │  │
│  │  (Next.js + shadcn)   │  │  Chat + Tool Renders   │  │
│  └───────────────────────┘  └──────────┬─────────────┘  │
└─────────────────────────────────────────┼───────────────┘
                                          │ AG-UI (SSE)
                              ┌───────────▼───────────────┐
                              │  FastAPI Backend           │
                              │  ┌──────────────────────┐  │
                              │  │  MAF HandoffBuilder   │  │
                              │  │  Triage → Specialists │  │
                              │  │  (Task / Calendar)    │  │
                              │  └──────────────────────┘  │
                              └────────────────────────────┘
```

## Project Structure

```
maf_copilotkit/
├── agent/                    # Python backend
│   ├── server.py             # FastAPI entrypoint
│   ├── agui_endpoint.py      # AG-UI / CopilotKit bridge
│   ├── config.py             # Pydantic settings
│   ├── agents/               # MAF agent definitions
│   │   ├── triage_agent.py   # Coordinator (routes requests)
│   │   ├── task_agent.py     # Task & docs specialist
│   │   └── calendar_agent.py # Calendar specialist
│   ├── tools/                # Tool implementations
│   │   ├── task_tools.py     # get_tasks, search_docs
│   │   └── calendar_tools.py # list_events, create_meeting
│   └── orchestration/        # Workflow definitions
│       └── handoff_workflow.py
├── web/                      # Next.js frontend
│   └── src/
│       ├── app/
│       │   ├── layout.tsx    # CopilotKit provider + Teams init
│       │   ├── page.tsx      # CopilotSidebar + workspace
│       │   └── globals.css   # Tailwind + dark theme
│       └── components/
│           ├── workspace.tsx       # Project dashboard
│           ├── tool-renderers.tsx  # Custom tool UI renderers
│           └── teams-initializer.tsx
├── docs/
│   └── a2ui-integration.md  # Future A2UI guide
└── README.md
```

## Quickstart

### Prerequisites

- Python ≥ 3.11 + [uv](https://github.com/astral-sh/uv)
- Node.js ≥ 18 + [pnpm](https://pnpm.io)
- OpenAI API key

### 1. Backend

```bash
cd agent
cp .env.example .env
# Edit .env → set OPENAI_API_KEY

uv venv
source .venv/bin/activate
uv pip install -e .

uvicorn server:app --reload --port 8000
```

The AG-UI endpoint is at `http://localhost:8000/copilotkit`.

### 2. Frontend

```bash
cd web
pnpm install
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) — the CopilotKit sidebar appears on the right.

### 3. Try It!

Type any of these in the chat:
- *"Show me my tasks"*
- *"What meetings do I have this week?"*
- *"Schedule a meeting for Friday at 2pm"*
- *"Search for architecture documents"*

## Teams Local Development

1. Start both backend and frontend (above)
2. Create a tunnel: `devtunnel create --allow-anonymous`
3. Forward port 3000: `devtunnel port create -p 3000`
4. Update `teams-manifest.json` — replace `{{YOUR-TUNNEL-URL}}` with tunnel URL
5. Zip the manifest and sideload into Teams
6. The app loads in a Teams personal tab

See [Teams Developer Docs](https://learn.microsoft.com/en-us/microsoftteams/platform/tabs/how-to/create-personal-tab) for details.

## Technology Stack

| Layer         | Technology                      |
|---------------|---------------------------------|
| Agent         | Microsoft Agent Framework (MAF) |
| Orchestration | MAF HandoffBuilder              |
| Protocol      | AG-UI (SSE)                     |
| Backend       | FastAPI + Uvicorn               |
| Frontend      | Next.js 15 + React 19           |
| Chat UI       | CopilotKit V2                   |
| Styling       | TailwindCSS v4                  |
| UI Components | shadcn/ui + Lucide icons        |
| Platform      | Microsoft Teams SDK             |

## A2UI Integration

See [docs/a2ui-integration.md](docs/a2ui-integration.md) for the future A2UI + AG-UI integration guide and migration path.
