import React from "react";
import { useState } from "react";
import { Search } from "lucide-react";
import { searchStudyKit } from "../lib/api";

export default function SearchTab({ jobId }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch(event) {
    event.preventDefault();

    if (!query.trim()) return;

    setIsSearching(true);
    setError("");

    try {
      const data = await searchStudyKit({
        jobId,
        query,
        topK: 5,
      });
      setResults(data.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSearching(false);
    }
  }

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <form onSubmit={handleSearch} className="flex flex-col gap-3 md:flex-row">
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Ask something from the lecture, like what is a sigmoid function?"
          className="min-h-12 flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm outline-none transition focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
        />

        <button
          type="submit"
          disabled={isSearching || !query.trim()}
          className="inline-flex min-h-12 items-center justify-center gap-2 rounded-2xl bg-slate-950 px-6 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
        >
          <Search size={17} />
          {isSearching ? "Searching" : "Search"}
        </button>
      </form>

      {error && (
        <div className="mt-4 rounded-2xl bg-red-50 p-4 text-sm font-semibold text-red-700">
          {error}
        </div>
      )}

      <div className="mt-5 grid gap-4">
        {results.map((result, index) => (
          <article
            key={`${result.start}-${index}`}
            className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
          >
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-bold text-blue-700">
                {result.start_time} to {result.end_time}
              </span>
              <span className="text-xs font-semibold text-slate-500">
                Match score: {result.score.toFixed(3)}
              </span>
            </div>
            <p className="text-sm leading-6 text-slate-700">{result.text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
