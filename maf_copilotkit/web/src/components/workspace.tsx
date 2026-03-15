"use client";

import {
  CalendarDays,
  CheckCircle2,
  Clock,
  ListTodo,
  TrendingUp,
  Users,
} from "lucide-react";
import { WorkflowProgress } from "./workflow-progress";

/**
 * Workspace — main content area showing project dashboard cards.
 */
export function Workspace() {
  return (
    <main className="flex-1 overflow-auto bg-zinc-950 p-6 md:p-10">
      {/* Live progress card — visible only while the agent is executing a tool */}
      <WorkflowProgress />

      {/* Header */}
      <header className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-zinc-50">
          Project Dashboard
        </h1>
        <p className="mt-1 text-sm text-zinc-400">
          Welcome back! Use the chat assistant on the right to manage your
          projects, tasks, and calendar.
        </p>
      </header>

      {/* KPI Cards */}
      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          icon={<ListTodo className="h-5 w-5" />}
          label="Open Tasks"
          value="12"
          color="text-indigo-400"
          bgColor="bg-indigo-950/40"
        />
        <KpiCard
          icon={<CheckCircle2 className="h-5 w-5" />}
          label="Completed"
          value="34"
          color="text-emerald-400"
          bgColor="bg-emerald-950/40"
        />
        <KpiCard
          icon={<CalendarDays className="h-5 w-5" />}
          label="Meetings This Week"
          value="4"
          color="text-sky-400"
          bgColor="bg-sky-950/40"
        />
        <KpiCard
          icon={<TrendingUp className="h-5 w-5" />}
          label="Sprint Progress"
          value="68%"
          color="text-amber-400"
          bgColor="bg-amber-950/40"
        />
      </div>

      {/* Recent Activity */}
      <section className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-6">
        <h2 className="mb-4 text-lg font-semibold text-zinc-100">
          Recent Activity
        </h2>
        <div className="space-y-3">
          <ActivityItem
            icon={<CheckCircle2 className="h-4 w-4 text-emerald-400" />}
            text="Dave Kim completed 'Set up CI/CD pipeline'"
            time="2 hours ago"
          />
          <ActivityItem
            icon={<Clock className="h-4 w-4 text-amber-400" />}
            text="Carol Singh moved 'Write API documentation' to In Review"
            time="4 hours ago"
          />
          <ActivityItem
            icon={<Users className="h-4 w-4 text-sky-400" />}
            text="Alice Chen scheduled 'Sprint Planning' for Monday"
            time="Yesterday"
          />
          <ActivityItem
            icon={<ListTodo className="h-4 w-4 text-indigo-400" />}
            text="Bob Martinez created 'Implement auth flow'"
            time="Yesterday"
          />
        </div>
      </section>

      {/* Tip */}
      <p className="mt-6 text-center text-xs text-zinc-600">
        💡 Try asking:{" "}
        <span className="text-zinc-400">
          &quot;Show me my tasks&quot;
        </span>{" "}
        or{" "}
        <span className="text-zinc-400">
          &quot;What meetings do I have this week?&quot;
        </span>
      </p>
    </main>
  );
}

/* ── Sub-components ───────────────────────────────────────────────────── */

function KpiCard({
  icon,
  label,
  value,
  color,
  bgColor,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
  bgColor: string;
}) {
  return (
    <div className={`rounded-xl border border-zinc-800 ${bgColor} p-5`}>
      <div className={`mb-2 ${color}`}>{icon}</div>
      <p className="text-2xl font-bold text-zinc-50">{value}</p>
      <p className="text-xs text-zinc-400">{label}</p>
    </div>
  );
}

function ActivityItem({
  icon,
  text,
  time,
}: {
  icon: React.ReactNode;
  text: string;
  time: string;
}) {
  return (
    <div className="flex items-start gap-3 rounded-lg px-3 py-2 transition-colors hover:bg-zinc-800/40">
      <div className="mt-0.5">{icon}</div>
      <div className="flex-1">
        <p className="text-sm text-zinc-200">{text}</p>
        <p className="text-xs text-zinc-500">{time}</p>
      </div>
    </div>
  );
}
