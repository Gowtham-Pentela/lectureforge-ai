import React, { useState } from "react";
import { Search, Loader2, Clock3, ExternalLink } from "lucide-react";
import { searchStudyKit } from "../lib/api";
import { buildYouTubeJumpUrl, formatTime } from "../lib/youtube";

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
      <div className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-5 shadow-[0_10px_24px_rgba(15,23,42,0.08)]">
        <div className="mb-4">
          <h3 className="font-serif text-2xl font-semibold text-[var(--app-text)]">
            Search the lecture
          </h3>

          <p className="mt-2 text-sm leading-6 text-[var(--app-muted)]">
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
            className="min-h-[44px] flex-1 rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] px-4 py-3 text-sm text-[var(--app-text)] shadow-sm outline-none transition placeholder:text-[var(--app-soft)] focus:border-[var(--app-accent)] focus:ring-2 focus:ring-[var(--app-accent-soft)]"
          />

          <button
            type="submit"
            disabled={isSearching || !query.trim() || !jobId}
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-md bg-[var(--app-accent)] px-5 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-[var(--app-accent-strong)] disabled:cursor-not-allowed disabled:bg-[var(--app-soft)]"
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
          <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}
      </div>

      {hasSearched && !isSearching && results.length === 0 && !error && (
        <div className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-5 text-sm text-[var(--app-muted)]">
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
                className="rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-5 shadow-[0_10px_24px_rgba(15,23,42,0.08)]"
              >
                <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                  <div className="inline-flex items-center gap-2 rounded bg-[var(--app-accent-soft)] px-2 py-1 font-mono text-xs font-bold text-[var(--app-accent-strong)]">
                    <Clock3 className="h-4 w-4" />
                    {result.start_time || formatTime(startSeconds)} -{" "}
                    {result.end_time || formatTime(endSeconds)}
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    {typeof result.score === "number" && (
                        <div className="rounded bg-[var(--app-panel-muted)] px-2 py-1 text-xs font-bold text-[var(--app-muted)]">
                        Relevance: {result.score.toFixed(2)}
                      </div>
                    )}

                    {jumpUrl && (
                      <a
                        href={jumpUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 rounded bg-[var(--app-panel-muted)] px-2 py-1 text-xs font-bold text-[var(--app-accent)] transition hover:bg-[var(--app-accent-soft)]"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                        Open at{" "}
                        {result.start_time || formatTime(startSeconds)}
                      </a>
                    )}
                  </div>
                </div>

                <p className="text-sm leading-7 text-[var(--app-text)]">
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
