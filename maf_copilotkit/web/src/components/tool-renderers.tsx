"use client";

import { useRenderTool } from "@copilotkit/react-core/v2";

/**
 * Registers custom renderers for backend tool calls.
 * CopilotKit will display these components instead of raw JSON
 * when the agent calls the corresponding tools.
 */
export function ToolRenderers() {
  // ── get_tasks ─────────────────────────────────────────────────────
  useRenderTool({
    name: "get_tasks",
    render: ({ args, result, status }) => {
      console.log("[get_tasks renderer] status:", status, "result:", result?.slice(0, 80));
      if (status !== "complete") {
        return (
          <div className="flex items-center gap-2 rounded-lg bg-zinc-800/60 px-4 py-3 text-sm text-zinc-300">
            <span className="animate-spin">⏳</span> Fetching tasks...
          </div>
        );
      }

      let data: { project?: string; tasks?: Array<Record<string, string>> } = {};
      try {
        data = JSON.parse(result ?? "{}");
      } catch {
        return <pre className="text-xs text-red-400">Failed to parse result</pre>;
      }

      const tasks = data.tasks ?? [];

      return (
        <div className="rounded-xl border border-zinc-700 bg-zinc-900 p-4">
          <h3 className="mb-3 text-sm font-semibold text-indigo-400">
            📋 Tasks — {data.project ?? args?.project ?? "Project"}
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-zinc-700 text-zinc-400">
                  <th className="pb-2 pr-3">ID</th>
                  <th className="pb-2 pr-3">Task</th>
                  <th className="pb-2 pr-3">Status</th>
                  <th className="pb-2 pr-3">Assignee</th>
                  <th className="pb-2 pr-3">Due</th>
                  <th className="pb-2">Priority</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((t, i) => (
                  <tr key={i} className="border-b border-zinc-800 text-zinc-200">
                    <td className="py-2 pr-3 font-mono text-indigo-300">{t.id}</td>
                    <td className="py-2 pr-3">{t.title}</td>
                    <td className="py-2 pr-3">
                      <StatusBadge status={t.status} />
                    </td>
                    <td className="py-2 pr-3">{t.assignee}</td>
                    <td className="py-2 pr-3 text-zinc-400">{t.due_date}</td>
                    <td className="py-2">
                      <PriorityBadge priority={t.priority} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    },
  });

  // ── search_docs ───────────────────────────────────────────────────
  useRenderTool({
    name: "search_docs",
    render: ({ result, status }) => {
      if (status !== "complete") {
        return (
          <div className="flex items-center gap-2 rounded-lg bg-zinc-800/60 px-4 py-3 text-sm text-zinc-300">
            <span className="animate-spin">⏳</span> Searching documents...
          </div>
        );
      }

      let data: { query?: string; documents?: Array<Record<string, string>> } = {};
      try {
        data = JSON.parse(result ?? "{}");
      } catch {
        return <pre className="text-xs text-red-400">Failed to parse result</pre>;
      }

      const docs = data.documents ?? [];

      return (
        <div className="rounded-xl border border-zinc-700 bg-zinc-900 p-4">
          <h3 className="mb-3 text-sm font-semibold text-emerald-400">
            📄 Documents matching &quot;{data.query}&quot;
          </h3>
          <div className="space-y-2">
            {docs.map((d, i) => (
              <div
                key={i}
                className="rounded-lg border border-zinc-800 bg-zinc-800/40 p-3"
              >
                <div className="flex items-center gap-2">
                  <span className="rounded bg-emerald-900/50 px-2 py-0.5 text-[10px] font-medium text-emerald-300">
                    {d.type}
                  </span>
                  <span className="text-xs text-zinc-400">{d.modified}</span>
                </div>
                <p className="mt-1 text-sm font-medium text-zinc-100">{d.title}</p>
                <p className="mt-0.5 text-xs text-zinc-400">{d.summary}</p>
              </div>
            ))}
          </div>
        </div>
      );
    },
  });

  // ── list_upcoming_events ──────────────────────────────────────────
  useRenderTool({
    name: "list_upcoming_events",
    render: ({ result, status }) => {
      console.log("[list_upcoming_events renderer] status:", status, "result:", result?.slice(0, 80));
      if (status !== "complete") {
        return (
          <div className="flex items-center gap-2 rounded-lg bg-zinc-800/60 px-4 py-3 text-sm text-zinc-300">
            <span className="animate-spin">⏳</span> Loading calendar...
          </div>
        );
      }

      let data: { events?: Array<Record<string, string>> } = {};
      try {
        data = JSON.parse(result ?? "{}");
      } catch {
        return <pre className="text-xs text-red-400">Failed to parse result</pre>;
      }

      const events = data.events ?? [];

      return (
        <div className="rounded-xl border border-zinc-700 bg-zinc-900 p-4">
          <h3 className="mb-3 text-sm font-semibold text-sky-400">
            📅 Upcoming Events
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-zinc-700 text-zinc-400">
                  <th className="pb-2 pr-3">Date</th>
                  <th className="pb-2 pr-3">Time</th>
                  <th className="pb-2 pr-3">Subject</th>
                  <th className="pb-2 pr-3">Duration</th>
                  <th className="pb-2">Organizer</th>
                </tr>
              </thead>
              <tbody>
                {events.map((e, i) => (
                  <tr key={i} className="border-b border-zinc-800 text-zinc-200">
                    <td className="py-2 pr-3 text-zinc-400">{e.date}</td>
                    <td className="py-2 pr-3">{e.time}</td>
                    <td className="py-2 pr-3 font-medium text-sky-300">{e.subject}</td>
                    <td className="py-2 pr-3">{e.duration}</td>
                    <td className="py-2">{e.organizer}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    },
  });

  // ── create_meeting ────────────────────────────────────────────────
  useRenderTool({
    name: "create_meeting",
    render: ({ result, status }) => {
      if (status !== "complete") {
        return (
          <div className="flex items-center gap-2 rounded-lg bg-zinc-800/60 px-4 py-3 text-sm text-zinc-300">
            <span className="animate-spin">⏳</span> Creating meeting...
          </div>
        );
      }

      let data: Record<string, unknown> = {};
      try {
        data = JSON.parse(result ?? "{}");
      } catch {
        return <pre className="text-xs text-red-400">Failed to parse result</pre>;
      }

      return (
        <div className="rounded-xl border border-emerald-800 bg-emerald-950/40 p-4">
          <h3 className="mb-3 text-sm font-semibold text-emerald-400">
            ✅ Meeting Created Successfully
          </h3>
          <div className="space-y-1 text-xs text-zinc-200">
            <p><span className="text-zinc-400">Subject:</span> {String(data.subject)}</p>
            <p><span className="text-zinc-400">Date:</span> {String(data.date)} at {String(data.time)}</p>
            <p><span className="text-zinc-400">Duration:</span> {String(data.duration)}</p>
            <p><span className="text-zinc-400">Attendees:</span> {Array.isArray(data.attendees) ? data.attendees.join(", ") : String(data.attendees)}</p>
            <p>
              <span className="text-zinc-400">Teams Link:</span>{" "}
              <a
                href={String(data.teams_link)}
                className="text-sky-400 underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                Join Meeting
              </a>
            </p>
          </div>
        </div>
      );
    },
  });

  return null;
}

/* ── Helper badges ────────────────────────────────────────────────────── */

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    "Done": "bg-emerald-900/50 text-emerald-300",
    "In Progress": "bg-amber-900/50 text-amber-300",
    "In Review": "bg-sky-900/50 text-sky-300",
    "To Do": "bg-zinc-700 text-zinc-300",
  };
  return (
    <span className={`rounded px-2 py-0.5 text-[10px] font-medium ${colors[status] ?? colors["To Do"]}`}>
      {status}
    </span>
  );
}

function PriorityBadge({ priority }: { priority: string }) {
  const colors: Record<string, string> = {
    "High": "text-red-400",
    "Medium": "text-amber-400",
    "Low": "text-zinc-400",
  };
  return <span className={`text-[10px] font-medium ${colors[priority] ?? "text-zinc-400"}`}>{priority}</span>;
}
