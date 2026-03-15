import type { Metadata } from "next";
import "./globals.css";
import "@copilotkit/react-ui/styles.css";

import { CopilotKit } from "@copilotkit/react-core";
import { TeamsInitializer } from "@/components/teams-initializer";

export const metadata: Metadata = {
  title: "PM Copilot — MAF + CopilotKit",
  description:
    "AI Project Manager Assistant powered by Microsoft Agent Framework and CopilotKit",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const agentUrl =
    process.env.NEXT_PUBLIC_COPILOTKIT_URL ?? "/api/copilotkit";

  return (
    <html lang="en" className="dark">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-zinc-950 text-zinc-50 antialiased">
        <TeamsInitializer />
        <CopilotKit runtimeUrl={agentUrl} agent="default">
          {children}
        </CopilotKit>
      </body>
    </html>
  );
}
