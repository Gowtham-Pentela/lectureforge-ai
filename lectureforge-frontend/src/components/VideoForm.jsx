import React, { useState } from "react";
import { PlayCircle } from "lucide-react";

export default function VideoForm({ onSubmit, disabled }) {
  const [youtubeUrl, setYoutubeUrl] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    const cleanedUrl = youtubeUrl.trim();

    if (!cleanedUrl) {
      return;
    }

    onSubmit(cleanedUrl);
  }

  const isSubmitDisabled = disabled || !youtubeUrl.trim();

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label
          htmlFor="youtube-url"
          className="mb-2 block text-sm font-semibold text-slate-700"
        >
          YouTube lecture URL
        </label>

        <input
          id="youtube-url"
          type="url"
          value={youtubeUrl}
          onChange={(event) => setYoutubeUrl(event.target.value)}
          placeholder="https://www.youtube.com/watch?v=..."
          disabled={disabled}
          className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-100"
        />
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          The video is processed once in English. You can translate the study
          kit after it is generated.
        </p>

        <button
          type="submit"
          disabled={isSubmitDisabled}
          className="inline-flex items-center justify-center gap-2 rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          <PlayCircle className="h-5 w-5" />
          Generate Study Kit
        </button>
      </div>
    </form>
  );
}