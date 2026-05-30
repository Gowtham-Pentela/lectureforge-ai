import React, { useMemo, useState } from "react";
import Tabs from "./Tabs";
import OutlineTab from "./OutlineTab";
import SummariesTab from "./SummariesTab";
import FlashcardsTab from "./FlashcardsTab";
import ConceptMapTab from "./ConceptMapTab";
import SearchTab from "./SearchTab";
import LiveAgentPanel from "./LiveAgentPanel";
import { buildYouTubeEmbedUrl, buildYouTubeJumpUrl, formatTime } from "../lib/youtube";
import { Clock3, Layers3, Languages, Loader2 } from "lucide-react";

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
  translationProgress = {},
  generationStatus = null,
}) {
  const [activeTab, setActiveTab] = useState("outline");
  const embedUrl = useMemo(
    () => buildYouTubeEmbedUrl(sourceVideoUrl),
    [sourceVideoUrl]
  );
  const transcriptPreview = studyKit.transcript_chunks?.slice(0, 8) || [];
  const readySections = new Set(generationStatus?.ready_sections || []);
  const isStillGenerating =
    generationStatus?.status === "queued" || generationStatus?.status === "processing";
  const sectionReady = {
    outline: readySections.has("outline") || Boolean(studyKit.outline?.length),
    summaries:
      readySections.has("summaries") ||
      Boolean(studyKit.summaries?.short_summary),
    "mind-map":
      readySections.has("concept_map") ||
      Boolean(studyKit.concept_map?.nodes?.length),
    flashcards:
      readySections.has("flashcards") || Boolean(studyKit.flashcards?.length),
    search: generationStatus?.search_index_status === "ready",
  };

  return (
    <main className="-mx-4 -mb-6 border-t border-[var(--app-border)] sm:-mx-6">
      <section className="grid min-h-[calc(100vh-4rem)] lg:grid-cols-[50%_50%]">
        <div className="border-b border-[var(--app-border)] bg-[var(--app-panel)] px-4 py-5 sm:px-6 lg:border-b-0 lg:border-r">
          <div className="mb-5">
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.24em] text-[var(--app-soft)]">
              The lecture
            </p>

            <h1 className="max-w-4xl font-serif text-3xl font-semibold leading-tight text-[var(--app-text)]">
              {studyKit.lecture_title || "Generated Study Kit"}
            </h1>

            <div className="mt-3 flex flex-wrap gap-4 text-sm font-semibold text-[var(--app-muted)]">
              <span className="inline-flex items-center gap-1.5">
                <Clock3 className="h-4 w-4" />
                {studyKit.duration_time || "Unknown duration"}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Layers3 className="h-4 w-4" />
                {studyKit.outline?.length || 0} chapters
              </span>
              <span>{studyKit.key_concepts?.length || 0} concepts</span>
            </div>
          </div>

          <div className="overflow-hidden rounded-md border border-[var(--app-border)] bg-black shadow-[0_18px_45px_rgba(15,23,42,0.16)]">
            {embedUrl ? (
              <iframe
                title={studyKit.lecture_title || "Lecture video"}
                src={embedUrl}
                className="aspect-video w-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
              />
            ) : (
              <div className="grid aspect-video place-items-center bg-slate-950 px-6 text-center text-sm text-white">
                Video preview is available after a valid YouTube URL is
                processed.
              </div>
            )}
          </div>

          <div className="mt-5">
            <div className="mb-3 flex items-center justify-between gap-4">
              <p className="text-xs font-bold uppercase tracking-[0.24em] text-[var(--app-soft)]">
                Transcript
              </p>
              <p className="font-mono text-xs text-[var(--app-soft)]">
                click any line to jump
              </p>
            </div>

            <div className="max-h-[38vh] space-y-1 overflow-y-auto pr-1">
              {transcriptPreview.map((chunk, index) => {
                const startSeconds = Math.floor(Number(chunk.start || 0));
                const jumpUrl = buildYouTubeJumpUrl(sourceVideoUrl, startSeconds);

                return (
                  <a
                    key={`${chunk.start}-${index}`}
                    href={jumpUrl || undefined}
                    target={jumpUrl ? "_blank" : undefined}
                    rel={jumpUrl ? "noreferrer" : undefined}
                    className="grid grid-cols-[3.5rem_1fr] gap-4 border-l-2 border-transparent px-2 py-2 text-sm leading-6 text-[var(--app-text)] transition hover:border-[var(--app-accent)] hover:bg-[var(--app-panel-muted)]"
                  >
                    <span className="font-mono text-xs font-bold text-[var(--app-accent)]">
                      {chunk.start_time || formatTime(startSeconds)}
                    </span>
                    <span>{chunk.text}</span>
                  </a>
                );
              })}
            </div>
          </div>
        </div>

        <aside className="bg-[var(--app-panel-muted)]">
          <div className="flex min-h-16 flex-col gap-3 border-b border-[var(--app-border)] px-5 py-3 sm:flex-row sm:items-center sm:justify-between">
            <Tabs activeTab={activeTab} setActiveTab={setActiveTab} />

            <div className="flex shrink-0 items-center gap-2 rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] px-3 py-2 text-sm text-[var(--app-muted)]">
              <Languages className="h-4 w-4" />
              <select
                value={selectedLanguage}
                onChange={(event) => onLanguageChange(event.target.value)}
                disabled={isTranslating}
                className="bg-transparent font-semibold outline-none disabled:cursor-not-allowed"
              >
                {languages.map((language) => (
                  <option key={language} value={language}>
                    {language}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {isTranslating && (
            <div className="border-b border-[var(--app-border)] bg-[var(--app-panel)] px-5 py-3 text-sm font-semibold text-[var(--app-accent)]">
              Translating into {selectedLanguage}...
              <TranslationProgressInline progress={translationProgress} />
            </div>
          )}

          {isStillGenerating && (
            <div className="border-b border-[var(--app-border)] bg-[var(--app-panel)] px-5 py-3 text-sm font-semibold text-[var(--app-accent)]">
              <span className="inline-flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                {generationStatus?.message || "Generating the next section"}
              </span>
              <GenerationProgress readySections={readySections} />
            </div>
          )}

          <div className="h-[calc(100vh-8rem)] overflow-y-auto px-5 py-5">
            {activeTab === "outline" && (
              sectionReady.outline ? (
                <OutlineTab
                  outline={studyKit.outline || []}
                  sourceVideoUrl={sourceVideoUrl}
                />
              ) : (
                <SectionLoading title="Outline is being generated" />
              )
            )}

            {activeTab === "summaries" && (
              sectionReady.summaries ? (
                <SummariesTab summaries={studyKit.summaries} />
              ) : (
                <SectionLoading title="Summary is being generated" />
              )
            )}

            {activeTab === "flashcards" && (
              sectionReady.flashcards ? (
                <FlashcardsTab
                  flashcards={studyKit.flashcards || []}
                  sourceVideoUrl={sourceVideoUrl}
                />
              ) : (
                <SectionLoading title="Flashcards are being generated" />
              )
            )}

            {activeTab === "mind-map" && (
              sectionReady["mind-map"] ? (
                <ConceptMapTab
                  conceptMap={studyKit.concept_map}
                  outline={studyKit.outline || []}
                  keyConcepts={studyKit.key_concepts || []}
                  sourceVideoUrl={sourceVideoUrl}
                />
              ) : (
                <SectionLoading title="Mind map is being generated" />
              )
            )}

            {activeTab === "search" && (
              generationStatus?.search_index_status === "ready" ||
              generationStatus?.status === "completed" ? (
                <SearchTab
                  jobId={jobId}
                  selectedLanguage={selectedLanguage}
                  sourceVideoUrl={sourceVideoUrl}
                />
              ) : (
                <SectionLoading title="Search is being indexed in the background" />
              )
            )}

            {activeTab === "live-agent" && (
              <LiveAgentPanel
                jobId={jobId}
                studyKit={studyKit}
                activeTab={activeTab}
                selectedLanguage={selectedLanguage}
              />
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}

function GenerationProgress({ readySections }) {
  const steps = [
    ["transcript", "Transcript"],
    ["outline", "Outline"],
    ["summaries", "Summary"],
    ["concept_map", "Mind Map"],
    ["flashcards", "Flashcards"],
  ];

  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {steps.map(([id, label]) => {
        const ready = readySections.has(id);

        return (
          <span
            key={id}
            className={`rounded px-2 py-1 text-xs ${
              ready
                ? "bg-[var(--app-accent-soft)] text-[var(--app-accent)]"
                : "bg-[var(--app-panel-muted)] text-[var(--app-muted)]"
            }`}
          >
            {label}
          </span>
        );
      })}
    </div>
  );
}

function SectionLoading({ title }) {
  return (
    <div className="grid min-h-[22rem] place-items-center rounded-md border border-[var(--app-border)] bg-[var(--app-panel)] p-8 text-center">
      <div>
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-[var(--app-accent)]" />
        <h3 className="mt-4 font-serif text-2xl font-semibold text-[var(--app-text)]">
          {title}
        </h3>
        <p className="mt-2 text-sm text-[var(--app-muted)]">
          You can keep reading the transcript while this section is prepared.
        </p>
      </div>
    </div>
  );
}

function TranslationProgressInline({ progress }) {
  const doneCount = Object.values(progress).filter(
    (status) => status === "done" || status === "cached"
  ).length;
  const totalCount = Object.keys(progress).length || 1;

  return (
    <span className="ml-2 font-mono text-xs text-[var(--app-muted)]">
      {doneCount}/{totalCount} sections ready
    </span>
  );
}
