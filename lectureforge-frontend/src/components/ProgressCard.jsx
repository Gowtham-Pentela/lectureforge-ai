import React from "react";
import { Loader2, CheckCircle2, AlertTriangle } from "lucide-react";

export default function ProgressCard({ status }) {
  if (!status) return null;

  const isFailed = status.status === "failed";
  const isCompleted = status.status === "completed";

  return (
    <section className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-soft">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900">
            {isCompleted ? "Study kit ready" : isFailed ? "Processing failed" : "Building your study kit"}
          </h2>
          <p className="mt-1 text-sm text-slate-600">{status.message}</p>
        </div>

        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl ${
            isFailed
              ? "bg-red-50 text-red-600"
              : isCompleted
              ? "bg-emerald-50 text-emerald-600"
              : "bg-blue-50 text-blue-600"
          }`}
        >
          {isFailed ? (
            <AlertTriangle size={22} />
          ) : isCompleted ? (
            <CheckCircle2 size={22} />
          ) : (
            <Loader2 size={22} className="animate-spin" />
          )}
        </div>
      </div>

      <div className="h-3 overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            isFailed ? "bg-red-500" : isCompleted ? "bg-emerald-500" : "bg-blue-600"
          }`}
          style={{ width: `${status.progress || 0}%` }}
        />
      </div>

      <div className="mt-2 text-right text-xs font-semibold text-slate-500">
        {status.progress || 0}%
      </div>

      {isFailed && status.error && (
        <div className="mt-4 rounded-2xl border border-red-100 bg-red-50 p-4 text-sm leading-6 text-red-700">
          <p className="font-semibold">{status.error}</p>
          {status.can_continue_with_transcript && (
            <p className="mt-1 text-red-600">
              This video may be blocked for automated access. Try another public
              captioned lecture URL.
            </p>
          )}
        </div>
      )}
    </section>
  );
}
