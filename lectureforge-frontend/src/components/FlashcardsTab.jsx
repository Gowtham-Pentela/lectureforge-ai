import React from "react";
import { useState } from "react";
import { RotateCcw } from "lucide-react";

function Flashcard({ card, index }) {
  const [flipped, setFlipped] = useState(false);

  return (
    <button
      onClick={() => setFlipped((value) => !value)}
      className="min-h-52 rounded-3xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-1 hover:shadow-soft"
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700">
          Card {index + 1}
        </span>
        <span className="text-xs font-semibold text-slate-500">
          {card.timestamp_time}
        </span>
      </div>

      <p className="text-sm font-semibold uppercase tracking-wide text-slate-400">
        {flipped ? "Answer" : "Question"}
      </p>

      <p className="mt-3 text-lg font-bold leading-7 text-slate-900">
        {flipped ? card.answer : card.question}
      </p>

      <div className="mt-5 inline-flex items-center gap-2 text-xs font-semibold text-slate-500">
        <RotateCcw size={14} />
        Click to flip
      </div>
    </button>
  );
}

export default function FlashcardsTab({ flashcards }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {flashcards?.map((card, index) => (
        <Flashcard key={`${card.question}-${index}`} card={card} index={index} />
      ))}
    </div>
  );
}
