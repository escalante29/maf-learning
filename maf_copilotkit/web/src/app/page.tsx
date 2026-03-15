"use client";

import { CopilotSidebar } from "@copilotkit/react-ui";
import { useAgent } from "@copilotkit/react-core/v2";
import { Workspace } from "@/components/workspace";
import { ToolRenderers } from "@/components/tool-renderers";
import { AgentSuggestions } from "@/components/agent-suggestions";

export default function Home() {
  // Connect to the AG-UI agent named "default"
  useAgent({ agentId: "default" });

  return (
    <>
      {/* Register tool renderers so CopilotKit can display tool results */}
      <ToolRenderers />
      {/* Show contextual follow-up suggestions after each agent response */}
      <AgentSuggestions />

      <CopilotSidebar
        defaultOpen={true}
        labels={{
          title: "PM Copilot",
          initial:
            "👋 Hi! I'm PM Copilot, your AI project manager. Ask me about tasks, calendar events, or anything project-related!",
          placeholder: "Ask about your project...",
        }}
        className="copilotKitSidebar"
      >
        <Workspace />
      </CopilotSidebar>
    </>
  );
}
