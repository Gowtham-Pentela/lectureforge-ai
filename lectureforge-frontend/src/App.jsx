import React, { useState } from "react";
import {
  BrainCircuit,
  FileText,
  GraduationCap,
  Link2,
  ShieldCheck,
  Sparkles,
  Youtube,
} from "lucide-react";
import Header from "./components/Header";
import VideoForm from "./components/VideoForm";
import ProgressCard from "./components/ProgressCard";
import StudyDashboard from "./components/StudyDashboard";
import FacultyAuditDashboard from "./components/FacultyAuditDashboard";
import {
  processVideo,
  processFacultyAudit,
  getJobStatus,
  getStudyKit,
  getFacultyAudit,
  translateSection,
} from "./lib/api";

export default function App() {
  const [mode, setMode] = useState("student");
  const [jobId, setJobId] = useState(null);
  const [studyKit, setStudyKit] = useState(null);
  const [englishStudyKit, setEnglishStudyKit] = useState(null);
  const [facultyAudit, setFacultyAudit] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState("English");
  const [sourceVideoUrl, setSourceVideoUrl] = useState("");

  const [jobStatus, setJobStatus] = useState(null);
  const [error, setError] = useState("");
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationProgress, setTranslationProgress] = useState({});
  const [lectureFormKey, setLectureFormKey] = useState(0);
  const [theme, setTheme] = useState("light");

  function resetLectureWorkspace() {
    if (isProcessing || isTranslating) {
      return;
    }

    setJobId(null);
    setStudyKit(null);
    setEnglishStudyKit(null);
    setFacultyAudit(null);
    setSelectedLanguage("English");
    setSourceVideoUrl("");
    setJobStatus(null);
    setError("");
    setTranslationProgress({});
    setLectureFormKey((previous) => previous + 1);
  }

  async function handleProcessVideo(youtubeUrl) {
    try {
      setSourceVideoUrl(youtubeUrl);
      setError("");
      setStudyKit(null);
      setEnglishStudyKit(null);
      setFacultyAudit(null);
      setSelectedLanguage("English");
      setTranslationProgress({});
      setJobId(null);

      const initialStatus = {
        status: "queued",
        progress: 0,
        message:
          mode === "faculty"
            ? "Starting faculty audit"
            : "Starting video processing",
        error: null,
        can_continue_with_transcript: false,
      };

      setJobStatus(initialStatus);

      const response =
        mode === "faculty"
          ? await processFacultyAudit(youtubeUrl)
          : await processVideo(youtubeUrl);

      const newJobId = response.job_id;

      setJobId(newJobId);

      setJobStatus({
        status: response.status || "queued",
        progress: 0,
        message:
          response.message ||
          (mode === "faculty"
            ? "Faculty audit started"
            : "Video processing started"),
        error: null,
        can_continue_with_transcript: false,
      });

      pollJobStatus(newJobId, mode);
    } catch (err) {
      const failedStatus = {
        status: "failed",
        progress: 100,
        message: mode === "faculty" ? "Faculty audit failed" : "Processing failed",
        error: err.message || "Failed to process video",
        can_continue_with_transcript: false,
      };

      setJobStatus(failedStatus);
      setError(err.message || "Failed to process video");
    }
  }

  async function pollJobStatus(newJobId, requestedMode) {
    let attempts = 0;
    const maxAttempts = 180;

    const intervalId = setInterval(async () => {
      try {
        attempts += 1;

        const job = await getJobStatus(newJobId);

        setJobStatus({
          status: job.status,
          progress: job.progress || 0,
          message: job.message || "",
          error: job.error || null,
          error_code: job.error_code || null,
          can_continue_with_transcript:
            job.can_continue_with_transcript || false,
        });

        if (job.status === "completed") {
          clearInterval(intervalId);

          setJobId(newJobId);

          if (requestedMode === "faculty") {
            const audit = await getFacultyAudit(newJobId);

            setFacultyAudit(audit);
            setStudyKit(null);
            setEnglishStudyKit(null);
            setSelectedLanguage("English");
            setTranslationProgress({});

            setJobStatus({
              status: "completed",
              progress: 100,
              message: "Faculty audit ready",
              error: null,
              can_continue_with_transcript: false,
            });
          } else {
            const kit = await getStudyKit(newJobId);

            setEnglishStudyKit(kit);
            setStudyKit(kit);
            setFacultyAudit(null);
            setSelectedLanguage("English");
            setTranslationProgress({});

            setJobStatus({
              status: "completed",
              progress: 100,
              message: "Study kit ready",
              error: null,
              can_continue_with_transcript: false,
            });
          }
        }

        if (job.status === "failed") {
          clearInterval(intervalId);
          setError(job.error || "Processing failed");
        }

        if (attempts >= maxAttempts) {
          clearInterval(intervalId);

          const timeoutMessage =
            requestedMode === "faculty"
              ? "Faculty audit took too long. Please try a shorter lecture."
              : "Processing took too long. Please try a shorter lecture.";

          setJobStatus({
            status: "failed",
            progress: 100,
            message: "Processing timed out",
            error: timeoutMessage,
            can_continue_with_transcript: false,
          });

          setError(timeoutMessage);
        }
      } catch (err) {
        clearInterval(intervalId);

        const message = err.message || "Failed to check job status";

        setJobStatus({
          status: "failed",
          progress: 100,
          message: "Processing failed",
          error: message,
          can_continue_with_transcript: false,
        });

        setError(message);
      }
    }, 2500);
  }

  function handleModeChange(nextMode) {
    if (isProcessing || isTranslating) {
      return;
    }

    setMode(nextMode);
    setJobId(null);
    setStudyKit(null);
    setEnglishStudyKit(null);
    setFacultyAudit(null);
    setSelectedLanguage("English");
    setSourceVideoUrl("");
    setJobStatus(null);
    setError("");
    setTranslationProgress({});
    setLectureFormKey((previous) => previous + 1);
  }

  async function handleLanguageChange(language) {
    setSelectedLanguage(language);

    if (!englishStudyKit || !jobId) {
      return;
    }

    if (language === "English") {
      setStudyKit(englishStudyKit);
      setTranslationProgress({});
      setIsTranslating(false);
      setError("");
      return;
    }

    const baseTranslatedKit = structuredCloneSafe(englishStudyKit);

    baseTranslatedKit.bilingual_output = {
      source_language: "English",
      target_language: language,
    };

    setStudyKit(baseTranslatedKit);
    setIsTranslating(true);
    setError("");

    const initialProgress = {
      lecture_title: "waiting",
      outline: "waiting",
      summaries: "waiting",
      key_concepts: "waiting",
      flashcards: "waiting",
      concept_map: "waiting",
      transcript_chunks: "waiting",
    };

    setTranslationProgress(initialProgress);

    try {
      const orderedSections = [
        "lecture_title",
        "outline",
        "summaries",
        "key_concepts",
        "flashcards",
        "concept_map",
      ];

      for (const section of orderedSections) {
        setTranslationProgress((previous) => ({
          ...previous,
          [section]: "translating",
        }));

        const translated = await translateSection({
          jobId,
          targetLanguage: language,
          section,
        });

        const normalizedData = normalizeTranslatedSectionData(
          section,
          translated.data
        );

        setStudyKit((previousKit) => ({
          ...previousKit,
          [section]: normalizedData,
          bilingual_output: {
            source_language: "English",
            target_language: language,
          },
        }));

        setTranslationProgress((previous) => ({
          ...previous,
          [section]: translated.cached ? "cached" : "done",
        }));
      }

      await translateTranscriptInBatches(language);

      setIsTranslating(false);
    } catch (err) {
      setIsTranslating(false);
      setError(err.message || "Translation failed");
    }
  }

  async function translateTranscriptInBatches(language) {
    const batchSize = 5;
    const totalChunks = englishStudyKit?.transcript_chunks?.length || 0;

    if (!totalChunks) {
      setTranslationProgress((previous) => ({
        ...previous,
        transcript_chunks: "done",
      }));

      return;
    }

    setTranslationProgress((previous) => ({
      ...previous,
      transcript_chunks: `0/${totalChunks}`,
    }));

    const translatedTranscriptChunks = [];

    for (let batchStart = 0; batchStart < totalChunks; batchStart += batchSize) {
      const translated = await translateSection({
        jobId,
        targetLanguage: language,
        section: "transcript_chunks",
        batchStart,
        batchSize,
      });

      const normalizedTranscriptData = normalizeTranslatedSectionData(
        "transcript_chunks",
        translated.data
      );

      const batchData = Array.isArray(normalizedTranscriptData)
        ? normalizedTranscriptData
        : [];

      translatedTranscriptChunks.push(...batchData);

      setStudyKit((previousKit) => ({
        ...previousKit,
        transcript_chunks: [...translatedTranscriptChunks],
        bilingual_output: {
          source_language: "English",
          target_language: language,
        },
      }));

      const completed = Math.min(batchStart + batchSize, totalChunks);

      setTranslationProgress((previous) => ({
        ...previous,
        transcript_chunks: `${completed}/${totalChunks}`,
      }));
    }

    setTranslationProgress((previous) => ({
      ...previous,
      transcript_chunks: "done",
    }));
  }

  const isProcessing =
    jobStatus?.status === "queued" || jobStatus?.status === "processing";

  return (
    <div
      data-theme={theme}
      className="min-h-screen bg-[var(--app-bg)] text-[var(--app-text)]"
    >
      <Header
        onNewLecture={resetLectureWorkspace}
        onThemeToggle={() =>
          setTheme((currentTheme) =>
            currentTheme === "dark" ? "light" : "dark"
          )
        }
        theme={theme}
      />

      <main className="px-4 pb-6 sm:px-6">
        {!studyKit && !facultyAudit && !jobStatus && (
          <section className="relative mx-auto mb-8 min-h-[calc(100vh-8rem)] max-w-7xl overflow-hidden py-12 text-center sm:py-20">
            <FloatingHeroDecor />

            <div className="relative z-10 mx-auto flex max-w-5xl flex-col items-center">
              <div className="mb-7 rounded-full border-4 border-[var(--app-red)] bg-[var(--app-red-soft)] px-6 py-3 text-xl font-black text-[var(--app-red)] sm:text-2xl">
                YouTube Video Summarizer
              </div>

              <h1 className="max-w-5xl text-6xl font-black leading-[0.98] tracking-[-0.055em] text-black sm:text-7xl lg:text-8xl">
                Instant YouTube Video Summarizer with Mind Maps
              </h1>

              <p className="mt-8 max-w-3xl text-2xl font-semibold leading-9 text-[var(--app-muted)]">
                Instantly create mind map summaries, study kits, and faculty
                reviews from any YouTube lecture.
              </p>

              <div className="mt-8 inline-flex rounded-2xl border border-[var(--app-border)] bg-white/75 p-1 shadow-sm">
                <ModePill
                  active={mode === "student"}
                  label="Study kit"
                  onClick={() => handleModeChange("student")}
                  disabled={isProcessing || isTranslating}
                />
                <ModePill
                  active={mode === "faculty"}
                  label="Faculty review"
                  onClick={() => handleModeChange("faculty")}
                  disabled={isProcessing || isTranslating}
                />
              </div>

              <div
                id="input"
                className="mt-10 w-full max-w-4xl"
              >
                <VideoForm
                  key={lectureFormKey}
                  onSubmit={handleProcessVideo}
                  disabled={isProcessing || isTranslating}
                  mode={mode}
                />
              </div>

              <SpeedUpgradeStats />
            </div>
          </section>
        )}

        {jobStatus &&
          (jobStatus.status === "queued" ||
            jobStatus.status === "processing" ||
            jobStatus.status === "failed") && (
            <div className="-mx-4 sm:-mx-6">
              <ProgressCard status={jobStatus} mode={mode} />
            </div>
          )}

        {error && jobStatus?.status !== "failed" && (
          <div className="mx-auto mb-6 max-w-5xl rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {mode === "student" && studyKit && (
          <StudyDashboard
            studyKit={studyKit}
            jobId={jobId}
            sourceVideoUrl={sourceVideoUrl}
            selectedLanguage={selectedLanguage}
            onLanguageChange={handleLanguageChange}
            isTranslating={isTranslating}
            translationProgress={translationProgress}
          />
        )}

        {mode === "faculty" && facultyAudit && (
          <FacultyAuditDashboard
            audit={facultyAudit}
            sourceVideoUrl={sourceVideoUrl}
          />
        )}
      </main>
    </div>
  );
}

function structuredCloneSafe(value) {
  if (typeof structuredClone === "function") {
    return structuredClone(value);
  }

  return JSON.parse(JSON.stringify(value));
}

function normalizeTranslatedSectionData(section, data) {
  if (section === "lecture_title") {
    if (typeof data === "string") {
      return data;
    }

    if (
      data &&
      typeof data === "object" &&
      typeof data.lecture_title === "string"
    ) {
      return data.lecture_title;
    }

    return "Generated Study Kit";
  }

  if (section === "summaries") {
    if (data && typeof data === "object" && data.summaries) {
      return data.summaries;
    }

    return data;
  }

  if (section === "outline") {
    if (data && typeof data === "object" && Array.isArray(data.outline)) {
      return data.outline;
    }

    return data;
  }

  if (section === "key_concepts") {
    if (
      data &&
      typeof data === "object" &&
      Array.isArray(data.key_concepts)
    ) {
      return data.key_concepts;
    }

    return data;
  }

  if (section === "flashcards") {
    if (data && typeof data === "object" && Array.isArray(data.flashcards)) {
      return data.flashcards;
    }

    return data;
  }

  if (section === "concept_map") {
    if (data && typeof data === "object" && data.concept_map) {
      return data.concept_map;
    }

    return data;
  }

  if (section === "transcript_chunks") {
    if (
      data &&
      typeof data === "object" &&
      Array.isArray(data.transcript_chunks)
    ) {
      return data.transcript_chunks;
    }

    return data;
  }

  return data;
}

function ModePill({ active, label, onClick, disabled }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`rounded-xl px-5 py-2.5 text-base font-bold transition disabled:cursor-not-allowed disabled:opacity-60 ${
        active
          ? "bg-[var(--app-accent)] text-white shadow-sm"
          : "text-[var(--app-muted)] hover:text-[var(--app-text)]"
      }`}
    >
      {label}
    </button>
  );
}

function FloatingHeroDecor() {
  return (
    <div className="pointer-events-none absolute inset-0 hidden lg:block">
      <div className="absolute left-0 top-24 rotate-[-14deg] rounded-2xl bg-white px-9 py-6 text-4xl font-black italic text-black shadow-[0_18px_50px_rgba(0,0,0,0.12)]">
        YouTube
      </div>

      <div className="absolute left-20 top-[18rem] rotate-[13deg] overflow-hidden rounded-2xl border-[10px] border-white bg-slate-900 shadow-[0_20px_55px_rgba(0,0,0,0.18)]">
        <div className="grid h-24 w-44 place-items-center bg-gradient-to-br from-slate-900 via-blue-950 to-indigo-700">
          <div className="grid h-12 w-12 place-items-center rounded-full bg-white/90 text-[var(--app-accent)]">
            <Youtube className="h-6 w-6 fill-current" />
          </div>
        </div>
      </div>

      <div className="absolute right-2 top-24 rotate-[-17deg] overflow-hidden rounded-2xl border-[10px] border-white bg-slate-100 shadow-[0_20px_55px_rgba(0,0,0,0.16)]">
        <div className="grid h-24 w-44 place-items-center bg-gradient-to-br from-white via-slate-100 to-slate-300">
          <div className="text-3xl font-black text-slate-700">E=mc²</div>
        </div>
      </div>

      <div className="absolute right-24 top-[21rem] rotate-[-10deg] rounded-3xl bg-[var(--app-red)] p-5 text-white shadow-[0_18px_40px_rgba(239,52,52,0.28)]">
        <Youtube className="h-12 w-12" />
      </div>

      <div className="absolute left-[18%] top-[21rem] h-14 w-20 rounded-l-2xl border-l-4 border-t-4 border-[var(--app-red)]" />
      <div className="absolute right-[12%] top-[21rem] h-1 w-28 rounded-full bg-[var(--app-red)]" />
    </div>
  );
}

function MapifyPreview() {
  const branches = [
    {
      title: "Extract transcript",
      icon: <Youtube className="h-4 w-4" />,
      nodes: ["Captions", "Chapters", "Timestamps"],
      className: "left-[5%] top-[14%]",
    },
    {
      title: "Build mind map",
      icon: <BrainCircuit className="h-4 w-4" />,
      nodes: ["Main ideas", "Dependencies", "Cross-links"],
      className: "right-[3%] top-[20%]",
    },
    {
      title: "Create study assets",
      icon: <FileText className="h-4 w-4" />,
      nodes: ["Summary", "Flashcards", "Search"],
      className: "left-[10%] bottom-[11%]",
    },
    {
      title: "Open workspace",
      icon: <Link2 className="h-4 w-4" />,
      nodes: ["Watch", "Ask", "Review"],
      className: "right-[8%] bottom-[9%]",
    },
  ];

  return (
    <div className="relative min-h-[560px] overflow-hidden rounded-[2rem] border border-[var(--app-border)] bg-[radial-gradient(circle_at_50%_45%,var(--app-accent-soft),transparent_34%),var(--app-panel)] p-6 shadow-[0_30px_90px_rgba(15,23,42,0.12)]">
      <div className="absolute left-1/2 top-1/2 z-10 w-48 -translate-x-1/2 -translate-y-1/2 rounded-3xl border border-[var(--app-accent)] bg-[var(--app-panel)] p-5 text-center shadow-[0_22px_60px_rgba(37,99,235,0.20)]">
        <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-2xl bg-[var(--app-accent)] text-white">
          <BrainCircuit className="h-6 w-6" />
        </div>
        <div className="font-serif text-xl font-semibold text-[var(--app-text)]">
          LectureForge map
        </div>
        <p className="mt-1 text-xs leading-5 text-[var(--app-muted)]">
          One link becomes a connected learning graph.
        </p>
      </div>

      <svg
        className="absolute inset-0 h-full w-full text-[var(--app-accent)] opacity-70"
        viewBox="0 0 720 560"
        role="img"
        aria-label="Mind map preview connections"
      >
        <path d="M360 280 C250 170 170 130 95 120" fill="none" stroke="currentColor" strokeWidth="3" />
        <path d="M360 280 C470 160 555 135 650 155" fill="none" stroke="currentColor" strokeWidth="3" />
        <path d="M360 280 C250 390 170 430 105 445" fill="none" stroke="currentColor" strokeWidth="3" />
        <path d="M360 280 C478 388 560 426 635 430" fill="none" stroke="currentColor" strokeWidth="3" />
      </svg>

      {branches.map((branch) => (
        <div
          key={branch.title}
          className={`absolute z-20 w-52 rounded-2xl border border-[var(--app-border)] bg-[var(--app-panel)] p-4 shadow-[0_18px_45px_rgba(15,23,42,0.10)] ${branch.className}`}
        >
          <div className="mb-3 flex items-center gap-2 font-serif text-lg font-semibold text-[var(--app-text)]">
            <span className="grid h-8 w-8 place-items-center rounded-xl bg-[var(--app-accent-soft)] text-[var(--app-accent)]">
              {branch.icon}
            </span>
            {branch.title}
          </div>

          <div className="grid gap-2">
            {branch.nodes.map((node) => (
              <div
                key={node}
                className="rounded-xl border border-[var(--app-border)] bg-[var(--app-panel-muted)] px-3 py-2 text-sm font-semibold text-[var(--app-muted)]"
              >
                {node}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function SpeedUpgradeStats() {
  return (
    <div className="mt-6 grid max-w-2xl gap-3 sm:grid-cols-3">
      <StatCard value="4 -> 2" label="core generation calls" />
      <StatCard value="-50%" label="LLM round trips" />
      <StatCard value="-67%" label="study asset calls" />
    </div>
  );
}

function StatCard({ value, label }) {
  return (
    <div className="rounded-2xl border border-[var(--app-border)] bg-[var(--app-panel)] px-4 py-3">
      <div className="font-serif text-2xl font-semibold text-[var(--app-text)]">
        {value}
      </div>
      <div className="mt-1 text-xs font-bold uppercase tracking-[0.18em] text-[var(--app-soft)]">
        {label}
      </div>
    </div>
  );
}
