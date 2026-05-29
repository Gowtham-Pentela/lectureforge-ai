import React, { useState } from "react";
import { RotateCcw, Clock3, ExternalLink } from "lucide-react";
import { buildYouTubeJumpUrl, formatTime } from "../lib/youtube";

export default function FlashcardsTab({
  flashcards = [],
  sourceVideoUrl = "",
}) {
  const [flippedCards, setFlippedCards] = useState({});

  if (!flashcards.length) {
    return (
      <div className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-5 text-sm text-[var(--app-muted)]">
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
            className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-5 shadow-[0_10px_24px_rgba(15,23,42,0.08)]"
          >
            <div className="mb-4 flex items-start justify-between gap-3">
              <div className="inline-flex items-center gap-2 rounded bg-[var(--app-accent-soft)] px-2 py-1 font-mono text-xs font-bold text-[var(--app-accent-strong)]">
                <Clock3 className="h-4 w-4" />
                Source: {card.timestamp_time || formatTime(timestampSeconds)}
              </div>

              {jumpUrl && (
                <a
                  href={jumpUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 rounded bg-[var(--app-panel-muted)] px-2 py-1 text-xs font-bold text-[var(--app-accent)] transition hover:bg-[var(--app-accent-soft)]"
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
              <div className="min-h-[150px] rounded-md border border-[var(--app-border)] bg-[var(--app-panel-muted)] p-4 transition hover:border-[var(--app-accent)]">
                <p className="mb-2 text-xs font-bold uppercase tracking-[0.2em] text-[var(--app-accent)]">
                  {isFlipped ? "Answer" : "Question"}
                </p>

                <p className="font-serif text-lg leading-7 text-[var(--app-text)]">
                  {isFlipped ? card.answer : card.question}
                </p>
              </div>
            </button>

            <div className="mt-4 flex items-center justify-between gap-3">
              <p className="text-xs text-[var(--app-muted)]">
                Click the card to reveal {isFlipped ? "question" : "answer"}.
              </p>

              <button
                type="button"
                onClick={() => toggleCard(index)}
                className="inline-flex items-center gap-2 rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] px-3 py-2 text-xs font-bold text-[var(--app-muted)] transition hover:bg-[var(--app-panel-muted)]"
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
