import React, { useState } from "react";
import { ArrowRight, Youtube } from "lucide-react";

const quickTryLinks = [
  {
    label: "AI Roadmap Course Introduction",
    url: "https://youtu.be/LJfUgSpq2PQ?si=OAF-xoerKuaC-hvA",
  },
  {
    label: "The power of introverts | Susan Cain | TED",
    url: "https://www.youtube.com/watch?v=c0KYU2j0TM4",
  },
  {
    label: "How to speak so that people want to listen",
    url: "https://www.youtube.com/watch?v=eIho2S0ZahI",
  },
];

export default function VideoForm({ onSubmit, disabled }) {
  const [youtubeUrl, setYoutubeUrl] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    const cleanedUrl = youtubeUrl.trim();

    if (!cleanedUrl || disabled) {
      return;
    }

    onSubmit(cleanedUrl);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <div className="mx-auto max-w-4xl rounded-3xl bg-white p-5 shadow-[0_22px_70px_rgba(0,0,0,0.08)]">
        <div className="flex flex-col gap-4 sm:flex-row">
          <input
            id="youtube-url"
            type="url"
            value={youtubeUrl}
            onChange={(event) => setYoutubeUrl(event.target.value)}
            placeholder="Paste YouTube link here..."
            disabled={disabled}
            className="min-h-16 flex-1 rounded-2xl border-0 bg-white px-3 text-2xl font-bold text-black outline-none transition placeholder:text-[#cdd2dc] disabled:cursor-not-allowed disabled:bg-white"
          />

          <button
            type="submit"
            disabled={disabled || !youtubeUrl.trim()}
            className="inline-flex min-h-16 items-center justify-center gap-2 rounded-xl bg-[var(--app-accent)] px-7 text-xl font-black text-white shadow-sm transition hover:bg-[var(--app-accent-strong)] disabled:cursor-not-allowed disabled:bg-[var(--app-soft)]"
          >
            Generate Study Kit
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      <p className="mx-auto max-w-3xl text-sm leading-6 text-[var(--app-muted)]">
        The video is processed once in English. You can translate the study kit,
        explore a real-time mind map, and ask the live agent for help.
      </p>

      <div>
        <p className="mb-4 text-xl font-bold text-[var(--app-muted)]">
          Quick Try:
        </p>
        <div className="mx-auto flex max-w-6xl flex-wrap justify-center gap-4">
          {quickTryLinks.map((item) => (
            <button
              key={item.url}
              type="button"
              onClick={() => setYoutubeUrl(item.url)}
              disabled={disabled}
              className="inline-flex max-w-sm items-center gap-3 truncate rounded-xl border border-[var(--app-border)] bg-white/50 px-5 py-3 text-left text-lg font-semibold text-slate-600 transition hover:border-[var(--app-accent)] hover:bg-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Youtube className="h-5 w-5 shrink-0 fill-[var(--app-red)] text-[var(--app-red)]" />
              <span className="truncate">{item.label}</span>
            </button>
          ))}
        </div>
      </div>
    </form>
  );
}
