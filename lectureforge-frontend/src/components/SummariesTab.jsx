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
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-5 flex flex-wrap gap-2">
        {summaryOptions.map((option) => (
          <button
            key={option.id}
            onClick={() => setSelected(option.id)}
            className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${
              selected === option.id
                ? "bg-slate-950 text-white"
                : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>

      <p className="whitespace-pre-line text-base leading-8 text-slate-700">
        {summaries?.[selected]}
      </p>
    </section>
  );
}
