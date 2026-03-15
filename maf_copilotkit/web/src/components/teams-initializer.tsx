"use client";

import { useEffect } from "react";

/**
 * Initializes the Microsoft Teams JavaScript SDK.
 * Gracefully skips if not running inside a Teams iframe.
 */
export function TeamsInitializer() {
  useEffect(() => {
    async function init() {
      try {
        const { app } = await import("@microsoft/teams-js");
        await app.initialize();

        // Get Teams context (theme, locale, etc.)
        const context = await app.getContext();
        const theme = context.app?.theme ?? "default";

        // Apply Teams theme to our app
        if (theme === "dark") {
          document.documentElement.classList.add("dark");
        } else if (theme === "default") {
          document.documentElement.classList.remove("dark");
        }

        // Notify Teams the tab has loaded
        app.notifySuccess();
      } catch {
        // Not running inside Teams — this is fine during local dev
        console.info("[TeamsInitializer] Not in Teams context, skipping SDK init.");
      }
    }

    init();
  }, []);

  return null;
}
