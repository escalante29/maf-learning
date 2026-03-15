"use client";

import { useCoAgent } from "@copilotkit/react-core";
import { CheckCircle2, Clock, Loader2 } from "lucide-react";

type StepStatus = "complete" | "in_progress" | "pending";

interface WorkflowStep {
  id: string;
  label: string;
  status: StepStatus;
}

interface WorkflowState {
  title?: string;
  steps?: WorkflowStep[];
}

/**
 * Reads live workflow state emitted by the backend (StateSnapshotEvent) and
 * renders a progress card while the agent is executing a tool.
 * Disappears automatically when the run finishes and state is cleared.
 */
export function WorkflowProgress() {
  const { state } = useCoAgent<WorkflowState>({ name: "default" });

  const steps = state?.steps ?? [];
  if (steps.length === 0) return null;

  const title = state?.title ?? "Working on it…";
  const completed = steps.filter((s) => s.status === _COMPLETE).length;
  const progressPct = Math.round((completed / steps.length) * 100);

  return (
    <div className="mb-6 rounded-xl border border-zinc-700 bg-zinc-900 p-5 shadow-lg">
      {/* Header */}
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-indigo-400">{title}</h3>
        <span className="text-xs text-zinc-400">
          {completed}/{steps.length} Complete
        </span>
      </div>

      {/* Progress bar */}
      <div className="mb-4 h-1.5 w-full overflow-hidden rounded-full bg-zinc-700">
        <div
          className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      {/* Steps */}
      <div className="space-y-2">
        {steps.map((step, i) => (
          <div key={step.id}>
            <div
              className={`flex items-center gap-3 rounded-lg border px-3 py-2.5 transition-colors ${
                step.status === _COMPLETE
                  ? "border-emerald-800/50 bg-emerald-950/30"
                  : step.status === _IN_PROGRESS
                  ? "border-indigo-700/50 bg-indigo-950/30"
                  : "border-zinc-800 bg-zinc-800/20"
              }`}
            >
              <StepIcon status={step.status} />
              <span
                className={`text-sm ${
                  step.status === _COMPLETE
                    ? "text-emerald-300"
                    : step.status === _IN_PROGRESS
                    ? "text-indigo-200"
                    : "text-zinc-500"
                }`}
              >
                {step.label}
              </span>
            </div>
            {/* Connector line between steps */}
            {i < steps.length - 1 && (
              <div className="ml-[22px] h-2 w-px bg-zinc-700" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function StepIcon({ status }: { status: StepStatus }) {
  if (status === _COMPLETE) {
    return <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-400" />;
  }
  if (status === _IN_PROGRESS) {
    return <Loader2 className="h-5 w-5 shrink-0 animate-spin text-indigo-400" />;
  }
  return <Clock className="h-5 w-5 shrink-0 text-zinc-600" />;
}

const _COMPLETE    = "complete";
const _IN_PROGRESS = "in_progress";
