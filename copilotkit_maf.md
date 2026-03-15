You are a senior full-stack engineer and AI platform architect specializing in **agentic applications for Microsoft ecosystems**.

Your task is to design and implement a **production-quality starter project** for an **Agentic application that runs inside a Microsoft Teams Tab**.

The stack must integrate the following technologies:

• Microsoft Agent Framework (MAF) for the backend agent
• AG-UI protocol for agent ↔ UI communication
• CopilotKit for the agent UI layer
• React + Next.js for the frontend
• TailwindCSS for styling
• shadcn/ui for UI components
• Microsoft Teams JavaScript SDK for embedding the app inside a Teams Tab

In the future we'll use A2UI + AG-UI so make sure the architecture is compatible with it and create a section describing the integration of both.

The result should be a **clean reference architecture suitable for enterprise development**.

The application must demonstrate the full pipeline:

User (Teams Tab)
→ React UI
→ CopilotKit
→ AG-UI
→ Microsoft Agent Framework agent
→ tool execution
→ streamed response
→ UI updates in the Teams tab.

---

PROJECT REQUIREMENTS

1. Architecture

Design a clear architecture with **two main services**.

backend/
MAF agent backend
AG-UI endpoint
tool definitions
streaming responses

frontend/
Next.js app rendered inside a Microsoft Teams tab
CopilotKit UI
AG-UI client connection
TailwindCSS styling
shadcn/ui components

Explain the responsibilities of each layer and how data flows through the system.

Include a simple architecture diagram.

---

2. Backend — Microsoft Agent Framework

Implement a minimal MAF agent that:

• exposes an **AG-UI compatible endpoint**
• supports **streaming responses**
• includes at least **one example tool** (example: weather lookup or document summarization)
• returns structured tool results that CopilotKit can render

Include:

• agent initialization
• tool registration
• AG-UI integration
• streaming responses
• server startup code

Explain how AG-UI messages are produced and sent to the frontend.

---

3. Frontend — Next.js + CopilotKit

Build a frontend React application that:

• runs inside a **Microsoft Teams Tab**
• connects to the backend via **AG-UI**
• renders a **CopilotKit chat assistant UI**
• streams agent responses
• renders tool results

Use:

• CopilotKit provider
• CopilotKit chat interface
• React functional components and hooks

---

4. Microsoft Teams Integration

Configure the frontend so it can run as a **Teams Tab application**.

Include:

• Teams SDK initialization
• Teams authentication considerations
• manifest configuration overview
• local development workflow for Teams

Explain how the Next.js app loads inside the Teams iframe environment.

---

5. UI Layer — TailwindCSS + shadcn/ui

Use **TailwindCSS** as the styling system.

Use **shadcn/ui** components for the layout and UI primitives.

The UI should include:

• responsive layout
• left panel or modal chat assistant
• main workspace area
• message bubbles
• loading indicators
• tool result cards

CopilotKit components should be styled using **Tailwind className overrides or wrapper components**.

Design the UI to look like a **modern developer tool interface** and be **dark-mode friendly**.

---

6. UX Features

Include the following behaviors:

• streaming responses from the agent
• tool execution visualization
• loading indicators
• graceful error handling
• retry / reconnect logic if the AG-UI stream disconnects

---

7. Project Structure

Provide a clean folder structure such as:

/agent
/backend code
/tools

/web
/pages or /app
/components
/copilot
/ui (shadcn)
/lib/agui

Explain the purpose of each directory.

---

8. Code Output

Provide **working code snippets** for:

• MAF agent setup
• tool implementation
• AG-UI endpoint
• CopilotKit integration
• Teams SDK initialization
• Tailwind setup
• shadcn/ui setup

---

9. Local Development

Include clear instructions to:

• install dependencies
• run backend agent
• run Next.js frontend
• configure Teams tab locally
• test the full pipeline

---

10. Output Format

Return your response organized into:

1. High-level architecture diagram
2. Folder structure
3. Backend implementation
4. Frontend implementation
5. Tailwind + shadcn setup
6. Microsoft Teams integration
7. AG-UI communication flow
8. Local run instructions

---

11. Extra considerations

1. For python always use a venv and prefer uv over plain pip.
2. For Node.js/Next.js prefer pnpm over npm.
3. Always use the latest stable version of each library.
4. Read the latest documentation you can find.
5. The folder you will output this project to will be: /Users/charlie/Documents/GitHub/maf-learning/maf_copilotkit
6. We need at least one Handoff MAF Workflow, leverage the example found in: /Users/charlie/Documents/GitHub/maf-learning/maf to get ideas.
7. Output a copy of your final plan to: Users/charlie/Documents/GitHub/maf-learning/maf_copilotkit/final_plan.md

---

12. Useful Documentation

https://docs.copilotkit.ai/microsoft-agent-framework
https://docs.copilotkit.ai/reference/v2
https://docs.copilotkit.ai/microsoft-agent-framework/prebuilt-components
https://docs.copilotkit.ai/microsoft-agent-framework/custom-look-and-feel/headless-ui
https://docs.copilotkit.ai/microsoft-agent-framework/generative-ui/tool-rendering
https://docs.copilotkit.ai/microsoft-agent-framework/generative-ui/state-rendering
https://docs.copilotkit.ai/microsoft-agent-framework/generative-ui/a2ui
https://docs.copilotkit.ai/microsoft-agent-framework/frontend-tools
https://github.com/CopilotKit/CopilotKit

https://docs.ag-ui.com/introduction
https://docs.ag-ui.com/sdk/python/core/overview

https://learn.microsoft.com/en-us/agent-framework/integrations/ag-ui/?pivots=programming-language-python
https://learn.microsoft.com/en-us/agent-framework/integrations/ag-ui/getting-started?pivots=programming-language-python
https://learn.microsoft.com/en-us/agent-framework/integrations/ag-ui/backend-tool-rendering?pivots=programming-language-python
https://github.com/microsoft/agent-framework/tree/main/python

https://dojo.ag-ui.com/microsoft-agent-framework-python/feature/agentic_chat?view=code&file=page.tsx
https://dojo.ag-ui.com/microsoft-agent-framework-python/feature/agentic_chat?view=code&file=dojo.py
https://dojo.ag-ui.com/microsoft-agent-framework-python/feature/shared_state?view=code&file=page.tsx
https://dojo.ag-ui.com/microsoft-agent-framework-python/feature/shared_state?view=code&file=style.css
https://dojo.ag-ui.com/microsoft-agent-framework-python/feature/shared_state?view=code&file=dojo.py

Focus on producing a **realistic developer starter template** that could be used as the foundation for a production agentic application inside Microsoft Teams.

Avoid theoretical discussion and focus on **concrete implementation guidance and working code**.
