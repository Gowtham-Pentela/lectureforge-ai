import React from "react";
import { Clock3, ExternalLink } from "lucide-react";

export default function OutlineTab({ outline = [], sourceVideoUrl = "" }) {
  if (!outline.length) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-5 text-sm text-slate-600 shadow-sm">
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
            className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="mb-3 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  <Clock3 className="h-4 w-4" />
                  {item.start_time || formatTime(startSeconds)} -{" "}
                  {item.end_time || formatTime(endSeconds)}
                </div>

                <h3 className="text-lg font-bold text-slate-950">
                  {item.title}
                </h3>
              </div>

              {jumpUrl && (
                <a
                  href={jumpUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center justify-center gap-2 rounded-2xl border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:border-blue-300 hover:bg-blue-100"
                >
                  <ExternalLink className="h-4 w-4" />
                  Open at {item.start_time || formatTime(startSeconds)}
                </a>
              )}
            </div>

            <p className="text-sm leading-7 text-slate-700">
              {item.summary}
            </p>
          </article>
        );
      })}
    </div>
  );
}

function buildYouTubeJumpUrl(url, startSeconds) {
  if (!url) {
    return "";
  }

  try {
    const parsedUrl = new URL(url);

    parsedUrl.searchParams.delete("t");
    parsedUrl.searchParams.delete("start");

    if (parsedUrl.hostname.includes("youtu.be")) {
      parsedUrl.searchParams.set("t", `${startSeconds}s`);
      return parsedUrl.toString();
    }

    if (parsedUrl.hostname.includes("youtube.com")) {
      parsedUrl.searchParams.set("t", `${startSeconds}s`);
      return parsedUrl.toString();
    }

    return "";
  } catch {
    return "";
  }
}

function formatTime(seconds) {
  if (
    seconds === null ||
    seconds === undefined ||
    Number.isNaN(Number(seconds))
  ) {
    return "00:00:00";
  }

  const totalSeconds = Math.floor(Number(seconds));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const secs = totalSeconds % 60;

  return [hours, minutes, secs]
    .map((value) => String(value).padStart(2, "0"))
    .join(":");
}