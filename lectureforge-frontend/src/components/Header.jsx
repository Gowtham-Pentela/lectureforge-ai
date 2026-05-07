import React from "react";
import { BrainCircuit, Sparkles } from "lucide-react";

export default function Header() {
  return (
    <header className="mb-8 flex flex-col gap-5 rounded-[2rem] bg-slate-950 px-6 py-8 text-white shadow-soft md:flex-row md:items-center md:justify-between md:px-8">
      <div>
        <div className="mb-3 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-sm text-blue-100">
          <Sparkles size={15} />
          AI study kit from YouTube lectures
        </div>
        <h1 className="text-3xl font-bold tracking-tight md:text-5xl">
          LectureForge AI
        </h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-slate-300">
          Paste a YouTube lecture URL. Get a timestamped outline, summaries,
          flashcards, a concept map, and semantic search.
        </p>
      </div>

      <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-blue-500/20">
        <BrainCircuit size={42} className="text-blue-200" />
      </div>
    </header>
  );
}
