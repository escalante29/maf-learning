# PM Copilot — LLM Context Document

> This document is designed for AI coding assistants (LLMs) to quickly understand the PM Copilot codebase. It provides structured metadata about every module, their relationships, data contracts, and conventions used throughout the application.

## Project Identity

- **Name:** PM Copilot
- **Purpose:** Multi-agent AI Project Manager Assistant for enterprise teams without a dedicated PM
- **Framework:** Microsoft Agent Framework (MAF) — Python, preview release
- **LLM Provider:** OpenAI (`gpt-4o` via `OpenAIChatClient`)
- **Orchestration Pattern:** Handoff (star topology — one coordinator, five specialists)
- **Location:** `maf/`
- **Python Version:** 3.10+
- **Virtual Environment:** `maf/.venv/`

---

## File Map

```
maf/
├── app.py                              # CLI entry point: --console, --server, --devui
├── config.py                           # Pydantic Settings from .env
├── requirements.txt                    # pip dependencies
├── .env.example                        # Environment variable template
├── README.md                           # Human-facing setup guide
│
├── agents/                             # Agent definitions (one file per agent)
│   ├── __init__.py
│   ├── triage.py                       # Coordinator — routes to specialists
│   ├── sharepoint_agent.py             # SharePoint CRUD operations
│   ├── meetings_agent.py              # Meeting transcripts + AI analysis
│   ├── calendar_agent.py              # Scheduling and calendar events
│   ├── documents_agent.py            # XLSX and PPTX generation
│   └── project_info_agent.py         # General PM knowledge (no tools)
│
├── tools/                              # @tool-decorated functions
│   ├── __init__.py
│   ├── graph_client.py                 # MS Graph auth — MockGraphClient or live
│   ├── sharepoint_tools.py            # 4 tools: list/create sites, create lists, upload
│   ├── meetings_tools.py             # 4 tools: list meetings, transcript, attendees, analyze
│   ├── calendar_tools.py             # 2 tools: create meeting, list events
│   └── document_tools.py             # 2 tools: create XLSX, create PPTX
│
├── orchestration/                      # Workflow wiring
│   ├── __init__.py
│   └── handoff_workflow.py            # HandoffBuilder connecting all 6 agents
│
├── bot/                                # MS Teams integration (scaffold)
│   ├── __init__.py
│   └── teams_bot.py                   # TeamsBot activity handler (placeholder)
│
├── templates/                          # XLSX/PPTX templates (future)
├── output/                             # Generated files written here at runtime
└── docs/
    ├── architecture_diagram.png        # Visual architecture diagram
    └── APPLICATION_FLOW.md             # Human developer onboarding guide
```

---

## Dependency Graph

```
app.py
  └── orchestration/handoff_workflow.py
        ├── config.py ← pydantic-settings, reads .env
        ├── agents/triage.py ← agent_framework.Agent, OpenAIChatClient
        ├── agents/sharepoint_agent.py
        │     └── tools/sharepoint_tools.py ← tools/graph_client.py
        ├── agents/meetings_agent.py
        │     └── tools/meetings_tools.py ← tools/graph_client.py
        ├── agents/calendar_agent.py
        │     └── tools/calendar_tools.py ← tools/graph_client.py
        ├── agents/documents_agent.py
        │     └── tools/document_tools.py ← openpyxl, python-pptx
        └── agents/project_info_agent.py (no tools)
```

---

## Module Reference

### config.py

| Export | Type | Description |
|---|---|---|
| `Settings` | `pydantic_settings.BaseSettings` | All config fields loaded from `.env` |
| `settings` | `Settings` instance | Singleton — import everywhere |
| `settings.openai_api_key` | `str` | OpenAI API key |
| `settings.openai_chat_model_id` | `str` | Model name, default `"gpt-4o"` |
| `settings.graph_mode` | `str` | `"mock"` or `"live"` |
| `settings.is_mock_mode` | `bool` property | `True` when graph_mode == "mock"` |
| `settings.azure_tenant_id` | `str` | Azure AD tenant (for live Graph) |
| `settings.azure_client_id` | `str` | Azure AD app client ID |
| `settings.azure_client_secret` | `str` | Azure AD app client secret |
| `settings.port` | `int` | Bot webhook port, default `3978` |

### tools/graph_client.py

| Export | Type | Description |
|---|---|---|
| `get_graph_client()` | `→ MockGraphClient \| GraphServiceClient` | Lazy singleton; checks `settings.is_mock_mode` |
| `MockGraphClient` | class | Returns realistic stub data for all Graph operations |

`MockGraphClient` methods:

| Method | Signature | Returns |
|---|---|---|
| `create_site` | `(name: str, description: str) → dict` | Site object with `id`, `displayName`, `webUrl` |
| `list_sites` | `() → list[dict]` | 3 mock sites (Project Alpha, Engineering Hub, HR Resources) |
| `create_list` | `(site_id, list_name, columns) → dict` | List object |
| `upload_file` | `(site_id, folder, filename) → dict` | File metadata with `webUrl` |
| `list_meetings` | `(user_id, days_back) → list[dict]` | 3 mock meetings (Sprint Planning, Design Review, Daily Standup) |
| `get_transcript` | `(meeting_id) → str` | Multi-line transcript text keyed by meeting ID |
| `get_attendees` | `(meeting_id) → list[str]` | Email addresses keyed by meeting ID |
| `create_event` | `(subject, start, end, attendees) → dict` | Calendar event with Teams `joinUrl` |
| `list_events` | `(user_id, days_ahead) → list[dict]` | 2 mock upcoming events |

### tools/ — Tool Functions

All tools follow the pattern:
```python
@tool(approval_mode="never_require")
def function_name(param: Annotated[str, "description"]) -> str:
    """Docstring — the LLM reads this to decide when to call the tool."""
    return json.dumps(result)
```

**sharepoint_tools.py** — 4 tools:

| Function | Parameters | Returns |
|---|---|---|
| `list_sharepoint_sites` | none | JSON array of site objects |
| `create_sharepoint_site` | `name: str, description: str` | JSON site object with `id`, `webUrl` |
| `create_sharepoint_list` | `site_id: str, list_name: str, columns: str` | JSON list object. `columns` is comma-separated |
| `upload_to_sharepoint` | `site_id: str, folder_path: str, file_name: str` | JSON file metadata |

**meetings_tools.py** — 4 tools:

| Function | Parameters | Returns |
|---|---|---|
| `list_recent_meetings` | `user_id: str = "me", days_back: int = 7` | JSON array of meeting objects |
| `get_meeting_transcript` | `meeting_id: str` | Raw transcript text (not JSON) |
| `get_meeting_attendees` | `meeting_id: str` | JSON array of email strings |
| `analyze_meeting_tasks` | `transcript_text: str` | JSON `{ total_tasks_found, tasks: [{speaker, task, raw_line}] }` |

**calendar_tools.py** — 2 tools:

| Function | Parameters | Returns |
|---|---|---|
| `create_meeting` | `subject, start_time, end_time, attendees` | JSON event object. `attendees` is comma-separated emails |
| `list_upcoming_events` | `user_id: str = "me", days_ahead: int = 7` | JSON array of event objects |

**document_tools.py** — 2 tools:

| Function | Parameters | Returns |
|---|---|---|
| `create_xlsx_report` | `title: str, data_json: str` | JSON `{ status, file_path, file_name, row_count }`. `data_json` format: `{"headers": [...], "rows": [[...]]}` |
| `create_pptx_presentation` | `title: str, subtitle: str, slides_json: str` | JSON `{ status, file_path, file_name, slide_count }`. `slides_json` format: `[{"title": "...", "bullets": ["..."]}]` |

Generated files are written to `maf/output/` with timestamp-based filenames.

### agents/ — Agent Definitions

Each module exports a single factory function:

| Module | Factory Function | Agent Name | Has Tools | Tool Source |
|---|---|---|---|---|
| `triage.py` | `create_triage_agent(client)` | `triage_agent` | No (handoff-only) | — |
| `sharepoint_agent.py` | `create_sharepoint_agent(client)` | `sharepoint_agent` | Yes (4) | `sharepoint_tools.py` |
| `meetings_agent.py` | `create_meetings_agent(client)` | `meetings_agent` | Yes (4) | `meetings_tools.py` |
| `calendar_agent.py` | `create_calendar_agent(client)` | `calendar_agent` | Yes (2) | `calendar_tools.py` |
| `documents_agent.py` | `create_documents_agent(client)` | `documents_agent` | Yes (2) | `document_tools.py` |
| `project_info_agent.py` | `create_project_info_agent(client)` | `project_info_agent` | No | — |

Factory signature: `(client: OpenAIChatClient | None = None) → Agent`
If `client` is `None`, a new `OpenAIChatClient` is created from `settings.openai_api_key`.

### orchestration/handoff_workflow.py

| Export | Signature | Description |
|---|---|---|
| `build_pm_workflow` | `(client: OpenAIChatClient \| None = None) → workflow` | Builds the complete Handoff orchestration |

**Workflow topology:**
- Start agent: `triage_agent`
- Handoff routes: `triage_agent → [sharepoint, meetings, calendar, documents, project_info]`
- Return routes: each specialist → `triage_agent`
- Termination: user message contains any of: `goodbye`, `bye`, `that's all`, `thank you`, `thanks, that's it`, `nothing else`, `exit`, `quit`

**MAF API calls used:**
```python
HandoffBuilder(name=, participants=, termination_condition=)
  .with_start_agent(agent)
  .add_handoff(source_agent, [target_agents])
  .build()
```

**Running the workflow:**
```python
# First message
async for event in workflow.run(user_input, stream=True): ...

# Subsequent responses
events = await workflow.run(responses={request_id: HandoffAgentUserRequest.create_response(text)})
```

### app.py

| Function | Description |
|---|---|
| `main()` | CLI parser, dispatches to `run_console()`, `run_server()`, or `run_devui()` |
| `run_console()` | Interactive terminal loop: `input()` → `workflow.run()` → `handle_events()` |
| `run_server()` | FastAPI app with `POST /api/messages` webhook (scaffold) |
| `run_devui()` | MAF DevUI launcher with fallback to console |
| `handle_events(events)` | Processes `WorkflowEvent` list, prints agent messages, returns pending `request_info` events |

**Event types handled by `handle_events()`:**
- `handoff_sent` → logs source → target transition
- `output` with `AgentResponse` → prints agent messages
- `output` with `list[Message]` → final conversation snapshot (suppressed)
- `request_info` with `HandoffAgentUserRequest` → prints agent message, collects for response loop
- `status` → suppressed in console mode

### bot/teams_bot.py

Scaffold only. `TeamsBot` class with `on_message_activity()` and `on_members_added_activity()` — both are `# TODO` placeholders for Bot Framework integration.

---

## Conventions

1. **All tool return types are `str`** — typically `json.dumps()` of a dict or list. The LLM parses the string.
2. **Agent names use `snake_case`** — these are used as identifiers in handoff tool names (`handoff_to_<name>`).
3. **Each agent module has one factory function** named `create_<name>_agent(client)`.
4. **Mock mode is default** — set `GRAPH_MODE=mock` in `.env`. No Azure credentials needed.
5. **sys.path** — When running from `maf/`, all imports are relative to the `maf/` root (e.g., `from tools.sharepoint_tools import ...`).
6. **Generated files** go to `maf/output/` with timestamp filenames: `report_YYYYMMDD_HHMMSS.xlsx`, `presentation_YYYYMMDD_HHMMSS.pptx`.

---

## Common Modification Patterns

### Adding a new specialist agent

1. Create `tools/new_tools.py` with `@tool`-decorated functions
2. Create `agents/new_agent.py` with `create_new_agent(client)` factory
3. In `orchestration/handoff_workflow.py`:
   - Import and instantiate the new agent
   - Add to `specialists` list
   - Add `.add_handoff(new_agent, [triage])` to the builder chain
4. Update triage agent instructions in `agents/triage.py` to include the new routing rule

### Adding a new tool to an existing agent

1. Add the `@tool`-decorated function in the corresponding `tools/*.py` module
2. Import it in the agent's `agents/*.py` module
3. Add it to the `tools=[...]` list in the `Agent()` constructor

### Switching from mock to live Graph

1. Set `GRAPH_MODE=live` in `.env`
2. Provide `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`
3. `graph_client.py` will automatically use `ClientSecretCredential` + `GraphServiceClient`
4. Replace `MockGraphClient` method calls in tool functions with actual `msgraph-sdk` API calls

### Changing the LLM model

Set `OPENAI_CHAT_MODEL_ID` in `.env`. To use different models per agent, pass separate `OpenAIChatClient(model_id=...)` instances to each factory function.
