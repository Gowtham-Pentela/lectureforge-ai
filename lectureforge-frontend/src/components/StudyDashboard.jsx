import React, { useState } from "react";
import Tabs from "./Tabs";
import OutlineTab from "./OutlineTab";
import SummariesTab from "./SummariesTab";
import FlashcardsTab from "./FlashcardsTab";
import ConceptMapTab from "./ConceptMapTab";
import SearchTab from "./SearchTab";
import TranscriptTab from "./TranscriptTab";

const tabs = [
  { id: "outline", label: "Outline" },
  { id: "summaries", label: "Summaries" },
  { id: "flashcards", label: "Flashcards" },
  { id: "concept-map", label: "Concept Map" },
  { id: "search", label: "Search" },
  { id: "transcript", label: "Transcript" },
];

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
  selectedLanguage,
  onLanguageChange,
  isTranslating,
}) {
  const [activeTab, setActiveTab] = useState("outline");

  function renderActiveTab() {
    if (activeTab === "outline") {
      return <OutlineTab outline={studyKit.outline || []} />;
    }

    if (activeTab === "summaries") {
      return <SummariesTab summaries={studyKit.summaries} />;
    }

    if (activeTab === "flashcards") {
      return <FlashcardsTab flashcards={studyKit.flashcards || []} />;
    }

    if (activeTab === "concept-map") {
      return <ConceptMapTab conceptMap={studyKit.concept_map} />;
    }

    if (activeTab === "search") {
      return <SearchTab jobId={jobId} />;
    }

    if (activeTab === "transcript") {
      return <TranscriptTab transcriptChunks={studyKit.transcript_chunks || []} />;
    }

    return null;
  }

  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-blue-600">
              Study Kit
            </p>

            <h2 className="mt-2 text-2xl font-bold text-slate-950">
              {studyKit.lecture_title || "Generated Study Kit"}
            </h2>

            <p className="mt-2 text-sm text-slate-600">
              Duration: {studyKit.duration_time || "Unknown"}
            </p>

            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              The lecture is processed once in English. Use the display language
              selector to translate the generated learning material without
              reprocessing the video.
            </p>

            {studyKit.bilingual_output?.target_language && (
              <p className="mt-2 text-sm font-medium text-blue-700">
                Displaying translated study kit in{" "}
                {studyKit.bilingual_output.target_language}
              </p>
            )}
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
          <div className="mt-5 rounded-2xl border border-blue-100 bg-blue-50 px-4 py-3 text-sm font-medium text-blue-700">
            Translating study kit into {selectedLanguage}...
          </div>
        )}
      </div>

      <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
        <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

        <div className="mt-6">
          {renderActiveTab()}
        </div>
      </div>
    </section>
  );
}