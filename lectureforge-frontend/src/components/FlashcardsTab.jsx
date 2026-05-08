import React, { useState } from "react";
import { RotateCcw, Clock3, ExternalLink } from "lucide-react";

export default function FlashcardsTab({
  flashcards = [],
  sourceVideoUrl = "",
}) {
  const [flippedCards, setFlippedCards] = useState({});

  if (!flashcards.length) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-5 text-sm text-slate-600 shadow-sm">
        No flashcards were generated for this lecture.
      </div>
    );
  }

  function toggleCard(index) {
    setFlippedCards((previous) => ({
      ...previous,
      [index]: !previous[index],
    }));
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {flashcards.map((card, index) => {
        const isFlipped = Boolean(flippedCards[index]);
        const timestampSeconds = Math.floor(Number(card.timestamp || 0));
        const jumpUrl = buildYouTubeJumpUrl(sourceVideoUrl, timestampSeconds);

        return (
          <article
            key={`${card.question}-${index}`}
            className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="mb-4 flex items-start justify-between gap-3">
              <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                <Clock3 className="h-4 w-4" />
                Source: {card.timestamp_time || formatTime(timestampSeconds)}
              </div>

              {jumpUrl && (
                <a
                  href={jumpUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 transition hover:bg-blue-100"
                >
                  <ExternalLink className="h-3.5 w-3.5" />
                  Open
                </a>
              )}
            </div>

            <button
              type="button"
              onClick={() => toggleCard(index)}
              className="w-full text-left"
            >
              <div className="min-h-[150px] rounded-2xl border border-slate-200 bg-slate-50 p-4 transition hover:border-blue-200 hover:bg-blue-50/40">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-blue-600">
                  {isFlipped ? "Answer" : "Question"}
                </p>

                <p className="text-sm leading-7 text-slate-800">
                  {isFlipped ? card.answer : card.question}
                </p>
              </div>
            </button>

            <div className="mt-4 flex items-center justify-between gap-3">
              <p className="text-xs text-slate-500">
                Click the card to reveal {isFlipped ? "question" : "answer"}.
              </p>

              <button
                type="button"
                onClick={() => toggleCard(index)}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
              >
                <RotateCcw className="h-4 w-4" />
                Flip
              </button>
            </div>
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