import React, { useState } from "react";
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
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Header />

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <section className="mb-8">
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6">
              <p className="text-sm font-semibold uppercase tracking-wide text-blue-600">
                LectureForge AI
              </p>

              <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
                {mode === "faculty"
                  ? "Improve lectures before students see them"
                  : "Turn YouTube lectures into study kits"}
              </h1>

              <p className="mt-3 max-w-3xl text-base leading-7 text-slate-600">
                {mode === "faculty"
                  ? "Paste a lecture URL to generate a private, instructor-facing audit across clarity, accessibility, equity, pacing, cognitive load, and student engagement."
                  : "Paste a YouTube lecture URL. LectureForge processes the video once in English, then progressively translates the generated study material section by section without reprocessing the video."}
              </p>
            </div>

            <div className="mb-6 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => handleModeChange("student")}
                disabled={isProcessing || isTranslating}
                className={`rounded-xl border px-4 py-2 text-sm font-semibold transition ${
                  mode === "student"
                    ? "border-slate-950 bg-slate-950 text-white"
                    : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
                } disabled:cursor-not-allowed disabled:opacity-60`}
              >
                Student Study Mode
              </button>

              <button
                type="button"
                onClick={() => handleModeChange("faculty")}
                disabled={isProcessing || isTranslating}
                className={`rounded-xl border px-4 py-2 text-sm font-semibold transition ${
                  mode === "faculty"
                    ? "border-slate-950 bg-slate-950 text-white"
                    : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
                } disabled:cursor-not-allowed disabled:opacity-60`}
              >
                Faculty Audit Mode
              </button>
            </div>

            <VideoForm
              onSubmit={handleProcessVideo}
              disabled={isProcessing || isTranslating}
              mode={mode}
            />

            {mode === "faculty" && (
              <p className="mt-4 text-sm leading-6 text-slate-500">
                Faculty reports are private, voluntary, and designed for lecture
                improvement only. They are not evaluations or surveillance.
              </p>
            )}
          </div>
        </section>

        {jobStatus &&
          (jobStatus.status === "queued" ||
            jobStatus.status === "processing" ||
            jobStatus.status === "failed") && (
            <div className="mb-6">
              <ProgressCard status={jobStatus} />
            </div>
          )}

        {error && jobStatus?.status !== "failed" && (
          <div className="mb-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
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
          <FacultyAuditDashboard audit={facultyAudit} />
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