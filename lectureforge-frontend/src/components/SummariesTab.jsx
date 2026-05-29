import React from "react";
import { useState } from "react";

const summaryOptions = [
  { id: "short_summary", label: "90 seconds" },
  { id: "medium_summary", label: "5 minutes" },
  { id: "full_summary", label: "Full" },
];

export default function SummariesTab({ summaries }) {
  const [selected, setSelected] = useState("short_summary");

  return (
    <section className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-5 shadow-[0_10px_24px_rgba(15,23,42,0.08)]">
      <div className="mb-5 flex flex-wrap gap-2">
        {summaryOptions.map((option) => (
          <button
            key={option.id}
            onClick={() => setSelected(option.id)}
            className={`rounded-md px-4 py-2 text-sm font-bold transition ${
              selected === option.id
                ? "bg-[var(--app-accent)] text-white"
                : "border border-[var(--app-border)] bg-[var(--app-panel)] text-[var(--app-muted)] hover:bg-[var(--app-panel-muted)]"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>

      <p className="whitespace-pre-line font-serif text-xl leading-9 text-[var(--app-text)]">
        {summaries?.[selected]}
      </p>
    </section>
  );
}
