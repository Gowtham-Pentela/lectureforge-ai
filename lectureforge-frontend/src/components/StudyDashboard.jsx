import React from "react";
import { useState } from "react";
import Tabs from "./Tabs";
import OutlineTab from "./OutlineTab";
import SummariesTab from "./SummariesTab";
import FlashcardsTab from "./FlashcardsTab";
import ConceptMapTab from "./ConceptMapTab";
import SearchTab from "./SearchTab";
import TranscriptTab from "./TranscriptTab";
import { Clock3, Layers3 } from "lucide-react";

export default function StudyDashboard({ jobId, studyKit }) {
  const [activeTab, setActiveTab] = useState("outline");

  return (
    <main className="mt-8">
      <section className="mb-5 rounded-[2rem] border border-slate-200 bg-white p-5 shadow-soft md:p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-600">
              Generated study kit
            </p>
            <h2 className="text-2xl font-bold text-slate-950 md:text-3xl">
              {studyKit.lecture_title}
            </h2>
          </div>

          <div className="flex flex-wrap gap-2">
            <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
              <Clock3 size={16} />
              {studyKit.duration_time}
            </div>
            <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
              <Layers3 size={16} />
              {studyKit.transcript_chunks?.length || 0} chunks
            </div>
          </div>
        </div>
      </section>

      <Tabs activeTab={activeTab} setActiveTab={setActiveTab} />

      {activeTab === "outline" && <OutlineTab outline={studyKit.outline} />}
      {activeTab === "summaries" && <SummariesTab summaries={studyKit.summaries} />}
      {activeTab === "flashcards" && <FlashcardsTab flashcards={studyKit.flashcards} />}
      {activeTab === "concept-map" && <ConceptMapTab conceptMap={studyKit.concept_map} />}
      {activeTab === "search" && <SearchTab jobId={jobId} />}
      {activeTab === "transcript" && <TranscriptTab chunks={studyKit.transcript_chunks} />}
    </main>
  );
}
