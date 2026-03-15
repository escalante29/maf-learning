"use client";

import { useCoAgent } from "@copilotkit/react-core";
import { useConfigureSuggestions } from "@copilotkit/react-core/v2";

interface Suggestion {
  title: string;
  message: string;
}

interface AgentState {
  suggestions?: Suggestion[];
}

/**
 * Reads follow-up suggestions emitted by the backend (StateSnapshotEvent) and
 * registers them as CopilotKit suggestion chips above the chat input.
 * Suggestions are set after each tool completes and cleared on the next run.
 */
export function AgentSuggestions() {
  const { state } = useCoAgent<AgentState>({ name: "default" });

  const suggestions = state?.suggestions ?? [];

  useConfigureSuggestions(
    suggestions.length > 0
      ? {
          suggestions,
          available: "after-first-message",
        }
      : null,
    [suggestions],
  );

  return null;
}
