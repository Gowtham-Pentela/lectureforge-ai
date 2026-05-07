import React, { useState } from "react";
import Tabs from "./Tabs";
import OutlineTab from "./OutlineTab";
import SummariesTab from "./SummariesTab";
import FlashcardsTab from "./FlashcardsTab";
import ConceptMapTab from "./ConceptMapTab";
import SearchTab from "./SearchTab";
import TranscriptTab from "./TranscriptTab";
import { Clock3, Layers3 } from "lucide-react";

const languages = [
  "English",
  "Hindi",
  "Telugu",
  "Spanish",
  "French",
  "Arabic",
  "Urdu",
];

export default function StudyDashboard({
  studyKit,
  jobId,
  sourceVideoUrl,
  selectedLanguage,
  onLanguageChange,
  isTranslating,
}) {
  const [activeTab, setActiveTab] = useState("outline");

  return (
    <main className="mt-8">
      <section className="mb-5 rounded-[2rem] border border-slate-200 bg-white p-5 shadow-soft md:p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-600">
              Generated study kit
            </p>

            <h2 className="text-2xl font-bold text-slate-950 md:text-3xl">
              {studyKit.lecture_title || "Generated Study Kit"}
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              The lecture is processed once in English. Use the display language
              selector to translate the generated learning material without
              reprocessing the video.
            </p>

            {studyKit.bilingual_output?.target_language && (
              <p className="mt-2 text-sm font-semibold text-blue-700">
                Displaying translated study kit in{" "}
                {studyKit.bilingual_output.target_language}
              </p>
            )}

            <div className="mt-4 flex flex-wrap gap-2">
              <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
                <Clock3 size={16} />
                {studyKit.duration_time || "Unknown duration"}
              </div>

              <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
                <Layers3 size={16} />
                {studyKit.transcript_chunks?.length || 0} chunks
              </div>
            </div>
          </div>

          <div className="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4 lg:w-80">
            <label className="mb-2 block text-sm font-semibold text-slate-700">
              Display language
            </label>

            <select
              value={selectedLanguage}
              onChange={(event) => onLanguageChange(event.target.value)}
              disabled={isTranslating}
              className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-100"
            >
              {languages.map((language) => (
                <option key={language} value={language}>
                  {language}
                </option>
              ))}
            </select>

            <p className="mt-2 text-xs leading-5 text-slate-500">
              Translation updates the generated study kit only. Transcript and
              semantic search remain based on the original English processing.
            </p>
          </div>
        </div>

        {isTranslating && (
          <div className="mt-5 rounded-2xl border border-blue-100 bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-700">
            Translating study kit into {selectedLanguage}...
          </div>
        )}
      </section>

      <Tabs activeTab={activeTab} setActiveTab={setActiveTab} />

      {activeTab === "outline" && (
        <OutlineTab
          outline={studyKit.outline || []}
          sourceVideoUrl={sourceVideoUrl}
        />
      )}

      {activeTab === "summaries" && (
        <SummariesTab summaries={studyKit.summaries} />
      )}

      {activeTab === "flashcards" && (
        <FlashcardsTab flashcards={studyKit.flashcards || []} />
      )}

      {activeTab === "concept-map" && (
        <ConceptMapTab conceptMap={studyKit.concept_map} />
      )}

      {activeTab === "search" && <SearchTab jobId={jobId} />}

      {activeTab === "transcript" && (
        <TranscriptTab chunks={studyKit.transcript_chunks || []} />
      )}
    </main>
  );
}