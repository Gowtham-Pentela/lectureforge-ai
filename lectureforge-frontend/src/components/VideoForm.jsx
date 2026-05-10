import React, { useState } from "react";

export default function VideoForm({ onSubmit, disabled, mode = "student" }) {
  const [youtubeUrl, setYoutubeUrl] = useState("");

  const isFacultyMode = mode === "faculty";

  function handleSubmit(event) {
    event.preventDefault();

    const cleanedUrl = youtubeUrl.trim();

    if (!cleanedUrl || disabled) {
      return;
    }

    onSubmit(cleanedUrl);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label
          htmlFor="youtube-url"
          className="block text-sm font-medium text-slate-700"
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
          className="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-100"
        />
      </div>

      <p className="text-sm leading-6 text-slate-500">
        {isFacultyMode
          ? "The lecture will be reviewed privately for clarity, accessibility, equity, pacing, cognitive load, and student engagement."
          : "The video is processed once in English. You can translate the study kit after it is generated."}
      </p>

      <button
        type="submit"
        disabled={disabled || !youtubeUrl.trim()}
        className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {isFacultyMode ? "Generate Faculty Audit" : "Generate Study Kit"}
      </button>
    </form>
  );
}