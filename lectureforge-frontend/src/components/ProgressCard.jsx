import React from "react";
import { AlertTriangle, CheckCircle2, Loader2 } from "lucide-react";

export default function ProgressCard({ status }) {
  if (!status) return null;

  const isFailed = status.status === "failed";
  const isCompleted = status.status === "completed";
  const title = isCompleted
    ? "Study kit ready"
    : isFailed
    ? "Processing failed"
    : "Processing your lecture";

  return (
    <section className="mx-auto grid min-h-[calc(100vh-9rem)] max-w-4xl place-items-center px-4 py-12 text-center">
      <div className="w-full rounded-[2rem] border border-[var(--app-border)] bg-white/90 px-6 py-10 shadow-[0_28px_90px_rgba(0,0,0,0.10)] sm:px-10">
        <div
          className={`mx-auto grid h-20 w-20 place-items-center rounded-3xl ${
            isFailed
              ? "bg-red-50 text-red-600"
              : isCompleted
              ? "bg-emerald-50 text-emerald-600"
              : "bg-[var(--app-accent-soft)] text-[var(--app-accent)]"
          }`}
        >
          {isFailed ? (
            <AlertTriangle size={34} />
          ) : isCompleted ? (
            <CheckCircle2 size={34} />
          ) : (
            <Loader2 size={38} className="animate-spin" />
          )}
        </div>

        <h2 className="mt-6 text-4xl font-black tracking-[-0.04em] text-black sm:text-5xl">
          {title}
        </h2>

        <p className="mx-auto mt-4 max-w-2xl text-lg font-semibold leading-8 text-[var(--app-muted)]">
          {status.message || "Processing your video. This can take a moment."}
        </p>

        {!isFailed && (
          <div className="mx-auto mt-8 max-w-xl">
            <div className="h-3 overflow-hidden rounded-full bg-[var(--app-red-soft)]">
              <div
                className="h-full rounded-full bg-[var(--app-accent)] transition-all duration-500"
                style={{ width: `${status.progress || 0}%` }}
              />
            </div>
            <div className="mt-3 font-mono text-sm font-bold text-[var(--app-muted)]">
              {status.progress || 0}% complete
            </div>
          </div>
        )}

        {isFailed && status.error && (
          <div className="mx-auto mt-6 max-w-2xl rounded-2xl border border-red-100 bg-red-50 p-4 text-sm leading-6 text-red-700">
            <p className="font-semibold">{status.error}</p>
            {status.can_continue_with_transcript && (
              <p className="mt-1 text-red-600">
                This video may be blocked for automated access. Try another
                public captioned lecture URL.
              </p>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
