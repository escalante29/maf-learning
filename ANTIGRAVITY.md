# ANTIGRAVITY Guide: MAF Learning Repository

Welcome to the `maf-learning` repository. This file serves as a comprehensive guide for LLMs and AI agents (like Antigravity) to rapidly understand the context, architecture, and conventions of this project.

## 1. Repository Context

This repository tracks learning progress and experimentation with the **Microsoft Agent Framework (MAF)** in 2026. It contains two main top-level directories:

*   **`maf/`**: The main application folder. It houses the **PM Copilot**, an enterprise-grade AI Project Manager Assistant built with MAF.
*   **`maf_examples_explained/`**: A documentation folder containing detailed markdown guides explaining various MAF features, patterns, and examples.

## 2. Project Architecture (`maf/` PM Copilot)

The PM Copilot application demonstrates the **Star-topology Handoff pattern**.

*   **Triage Agent** (`maf/agents/triage.py`): Acts as the central router and coordinator. It analyzes user intent and routes the conversation to the appropriate specialist agent.
*   **Specialist Agents**:
    *   `sharepoint_agent.py`: Manages SharePoint sites, lists, and files.
    *   `meetings_agent.py`: Handles transcripts, attendees, and meeting intelligence.
    *   `calendar_agent.py`: Manages calendar events and scheduling.
    *   `documents_agent.py`: Generates reports (XLSX) and presentations (PPTX).
    *   `project_info_agent.py`: Provides PM methodology advice and best practices.

**Workflow Engine**: The orchestration is wired together in `maf/orchestration/handoff_workflow.py` using `HandoffBuilder`.

## 3. Orchestration Evaluation Patterns

Inside the `maf/agents/` directory, you will find several subdirectories demonstrating different MAF orchestration strategies (used for learning and evaluation):

*   `01_handoff/`: The primary pattern used by PM Copilot (star topology).
*   `02_sequential/`: Agents passing work linearly.
*   `03_concurrent/`: Agents running tasks in parallel.
*   `04_group_chat/`: Broadcast or round-robin conversation models.
*   `05_magentic/`: Examples utilizing the Magentic framework features.

## 4. Important Technical Details

*   **Python Environment**: The project requires Python 3.10+. Dependencies should be installed in the virtual environment located at `maf/.venv`. The current `agent-framework` version is `1.0.0rc4`. Note that 1.0.0rc1 removed compatibility shims for `FunctionTool[Any]`, enforced explicit imports over wildcard imports, and standardized `source_id` for state providers. 1.0.0rc4 includes stability improvements and better AG-UI integration.
*   **Configuration**: Settings are loaded from `maf/.env` (use `maf/.env.example` as a template) and managed via `maf/config.py`.
    *   Pay special attention to the `GRAPH_MODE` environment variable (`mock` or `live`). This controls whether the tools interact with real Microsoft Graph APIs or use mocked data.
*   **Run Modes**: The application (`maf/app.py`) supports three execution modes:
    *   `python app.py --console`: Interactive terminal conversation.
    *   `python app.py --server`: Bot Framework webhook server (FastAPI) for MS Teams integration.
    *   `python app.py --devui`: Launches the built-in MAF Developer UI for visual debugging.

## 5. Coding Conventions for LLMs

When modifying or extending this codebase, adhere to the following rules:

1.  **Paths**: Always use relative paths when working within the repository (e.g., relative to `Agents2026/maf` or the repository root).
2.  **Security**: **NEVER** commit `.env` files, API keys, client secrets, or sensitive tenant information. Verify changes against `.gitignore` before proposing them.
3.  **Adding Features**:
    *   New tools (e.g., Graph API wrappers) belong in `maf/tools/`.
    *   New agents belong in `maf/agents/`.
    *   If a new agent needs to be part of the main PM Copilot flow, it **must** be added and wired up in `maf/orchestration/handoff_workflow.py`.
    *   Update `maf/README.md` and this `ANTIGRAVITY.md` file if architectural changes are made.
4.  **Formatting**: Ensure new Python code follows PEP 8. Use standard python docstrings for new tools.

## 6. Updating MAF (Microsoft Agent Framework)

Future LLMs should follow these steps when asked to update the `agent-framework`:
1.  **Check for Updates**: Review the [Microsoft Agent Framework GitHub Releases](https://github.com/microsoft/agent-framework/releases) for the target version and parse the release notes.
2.  **Identify Breaking Changes**: Specifically extract any `[BREAKING]` changes from the changelog (e.g., changes to types like `Message`, `FunctionTool`, state providers, or import structures).
3.  **Scan the Codebase**: Use `grep` or file search tools in the `maf/` directory to check if the repository utilizes the patterns affected by the breaking changes.
4.  **Install the Update**: Run `source maf/.venv/bin/activate && pip install agent-framework==<target_version>`.
5.  **Apply Fixes and Verify**: Apply any necessary code modifications and run `source maf/.venv/bin/activate && python maf/app.py --console` to verify the application starts without import or initialization errors.
6.  **Document**: Update this file (Section 4) with the newly installed version and any new framework constraints.

---

*Generated by Antigravity*
