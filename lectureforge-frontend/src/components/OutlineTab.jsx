import React from "react";
import { Clock3, ExternalLink } from "lucide-react";
import { buildYouTubeJumpUrl, formatTime } from "../lib/youtube";

export default function OutlineTab({ outline = [], sourceVideoUrl = "" }) {
  if (!outline.length) {
    return (
      <div className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-5 text-sm text-[var(--app-muted)]">
        No outline was generated for this lecture.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {outline.map((item, index) => {
        const startSeconds = Math.floor(Number(item.start || 0));
        const endSeconds = Math.floor(Number(item.end || 0));
        const jumpUrl = buildYouTubeJumpUrl(sourceVideoUrl, startSeconds);

        return (
          <article
            key={`${item.title}-${index}`}
            className="border-b border-[var(--app-border)] px-1 py-5 last:border-b-0"
          >
            <div className="mb-3 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div className="grid gap-3 sm:grid-cols-[2rem_1fr]">
                <div className="pt-1 font-mono text-sm font-bold text-[var(--app-muted)]">
                  {String(index + 1).padStart(2, "0")}
                </div>
                <div>
                  <div className="mb-2 inline-flex items-center gap-2 rounded bg-[var(--app-accent-soft)] px-2 py-1 font-mono text-xs font-bold text-[var(--app-accent-strong)]">
                  <Clock3 className="h-4 w-4" />
                  {item.start_time || formatTime(startSeconds)} -{" "}
                  {item.end_time || formatTime(endSeconds)}
                </div>

                  <h3 className="font-serif text-2xl font-semibold text-[var(--app-text)]">
                    {item.title}
                  </h3>
                </div>
              </div>

              {jumpUrl && (
                <a
                  href={jumpUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center justify-center gap-2 rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] px-3 py-2 text-sm font-bold text-[var(--app-accent)] transition hover:bg-[var(--app-panel-muted)]"
                >
                  <ExternalLink className="h-4 w-4" />
                  Open at {item.start_time || formatTime(startSeconds)}
                </a>
              )}
            </div>

            <p className="ml-0 text-lg leading-8 text-[var(--app-text)] sm:ml-11">
              {item.summary}
            </p>
          </article>
        );
      })}
    </div>
  );
}
