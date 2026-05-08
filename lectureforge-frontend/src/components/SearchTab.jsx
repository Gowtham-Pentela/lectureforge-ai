import React, { useState } from "react";
import { Search, Loader2, Clock3, ExternalLink } from "lucide-react";
import { searchStudyKit } from "../lib/api";

export default function SearchTab({
  jobId,
  selectedLanguage = "English",
  sourceVideoUrl = "",
}) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch(event) {
    event.preventDefault();

    const cleanedQuery = query.trim();

    if (!cleanedQuery || !jobId) {
      return;
    }

    try {
      setIsSearching(true);
      setError("");
      setHasSearched(true);

      const data = await searchStudyKit(
        jobId,
        cleanedQuery,
        5,
        selectedLanguage
      );

      setResults(Array.isArray(data.results) ? data.results : []);
    } catch (err) {
      setResults([]);
      setError(err.message || "Search failed");
    } finally {
      setIsSearching(false);
    }
  }

  return (
    <div className="space-y-5">
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="mb-4">
          <h3 className="text-lg font-bold text-slate-950">
            Search the lecture
          </h3>

          <p className="mt-1 text-sm leading-6 text-slate-600">
            Ask a question or search for a topic. If a translated language is
            selected, your query is translated to English for semantic search
            and the results are displayed in the selected language.
          </p>
        </div>

        <form
          onSubmit={handleSearch}
          className="flex flex-col gap-3 sm:flex-row"
        >
          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Example: How do you copy an array?"
            className="min-h-[44px] flex-1 rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          />

          <button
            type="submit"
            disabled={isSearching || !query.trim() || !jobId}
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {isSearching ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Searching
              </>
            ) : (
              <>
                <Search className="h-4 w-4" />
                Search
              </>
            )}
          </button>
        </form>

        {error && (
          <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}
      </div>

      {hasSearched && !isSearching && results.length === 0 && !error && (
        <div className="rounded-3xl border border-slate-200 bg-white p-5 text-sm text-slate-600 shadow-sm">
          No matching transcript chunks found. Try a different keyword or a
          broader question.
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          {results.map((result, index) => {
            const startSeconds = Math.floor(Number(result.start || 0));
            const endSeconds = Math.floor(Number(result.end || 0));
            const jumpUrl = buildYouTubeJumpUrl(sourceVideoUrl, startSeconds);

            return (
              <article
                key={`${result.start}-${index}`}
                className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm"
              >
                <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                  <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                    <Clock3 className="h-4 w-4" />
                    {result.start_time || formatTime(startSeconds)} -{" "}
                    {result.end_time || formatTime(endSeconds)}
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    {typeof result.score === "number" && (
                      <div className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                        Relevance: {result.score.toFixed(2)}
                      </div>
                    )}

                    {jumpUrl && (
                      <a
                        href={jumpUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 transition hover:bg-blue-100"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                        Open at{" "}
                        {result.start_time || formatTime(startSeconds)}
                      </a>
                    )}
                  </div>
                </div>

                <p className="text-sm leading-7 text-slate-700">
                  {result.text}
                </p>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}

function buildYouTubeJumpUrl(url, startSeconds) {
  if (!url) {
    return "";
  }

  try {
    const parsedUrl = new URL(url);

    parsedUrl.searchParams.delete("t");
    parsedUrl.searchParams.delete("start");

    if (parsedUrl.hostname.includes("youtu.be")) {
      parsedUrl.searchParams.set("t", `${startSeconds}s`);
      return parsedUrl.toString();
    }

    if (parsedUrl.hostname.includes("youtube.com")) {
      parsedUrl.searchParams.set("t", `${startSeconds}s`);
      return parsedUrl.toString();
    }

    return "";
  } catch {
    return "";
  }
}

function formatTime(seconds) {
  if (
    seconds === null ||
    seconds === undefined ||
    Number.isNaN(Number(seconds))
  ) {
    return "00:00:00";
  }

  const totalSeconds = Math.floor(Number(seconds));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const secs = totalSeconds % 60;

  return [hours, minutes, secs]
    .map((value) => String(value).padStart(2, "0"))
    .join(":");
}