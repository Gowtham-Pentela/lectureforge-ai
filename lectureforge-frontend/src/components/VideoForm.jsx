import React from "react";
import { PlayCircle, Languages } from "lucide-react";

export default function VideoForm({
  youtubeUrl,
  setYoutubeUrl,
  targetLanguage,
  setTargetLanguage,
  onSubmit,
  isLoading,
}) {
  return (
    <form
      onSubmit={onSubmit}
      className="rounded-[2rem] border border-slate-200 bg-white p-5 shadow-soft md:p-6"
    >
      <label className="mb-2 block text-sm font-semibold text-slate-700">
        YouTube lecture URL
      </label>

      <div className="flex flex-col gap-3 md:flex-row">
        <input
          value={youtubeUrl}
          onChange={(event) => setYoutubeUrl(event.target.value)}
          placeholder="https://www.youtube.com/watch?v=..."
          className="min-h-12 flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm outline-none transition focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
          disabled={isLoading}
        />

        <div className="relative md:w-56">
          <Languages
            size={17}
            className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
          />
          <select
            value={targetLanguage}
            onChange={(event) => setTargetLanguage(event.target.value)}
            className="min-h-12 w-full appearance-none rounded-2xl border border-slate-200 bg-slate-50 px-10 text-sm outline-none transition focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
            disabled={isLoading}
          >
            <option>English</option>
            <option>Spanish</option>
            <option>Hindi</option>
            <option>Telugu</option>
            <option>Arabic</option>
            <option>Chinese</option>
            <option>French</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={isLoading || !youtubeUrl.trim()}
          className="inline-flex min-h-12 items-center justify-center gap-2 rounded-2xl bg-blue-600 px-6 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
        >
          <PlayCircle size={18} />
          Generate
        </button>
      </div>

      <p className="mt-3 text-xs leading-5 text-slate-500">
        The backend first tries YouTube transcripts, then subtitle extraction,
        then Whisper fallback when audio access is available.
      </p>
    </form>
  );
}
