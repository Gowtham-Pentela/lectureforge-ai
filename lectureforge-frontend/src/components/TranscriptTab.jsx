import React from "react";
export default function TranscriptTab({ chunks }) {
  return (
    <div className="grid gap-3">
      {chunks?.map((chunk, index) => (
        <article
          key={`${chunk.start}-${index}`}
          className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
        >
          <div className="mb-2 text-xs font-bold text-blue-700">
            {chunk.start_time} to {chunk.end_time}
          </div>
          <p className="text-sm leading-6 text-slate-700">{chunk.text}</p>
        </article>
      ))}
    </div>
  );
}
