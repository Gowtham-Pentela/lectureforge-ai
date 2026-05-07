import React, { useState } from "react";
import Header from "./components/Header";
import VideoForm from "./components/VideoForm";
import ProgressCard from "./components/ProgressCard";
import StudyDashboard from "./components/StudyDashboard";
import {
  processVideo,
  getJobStatus,
  getStudyKit,
  translateStudyKit,
} from "./lib/api";

export default function App() {
  const [jobId, setJobId] = useState(null);
  const [studyKit, setStudyKit] = useState(null);
  const [englishStudyKit, setEnglishStudyKit] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState("English");
  const [sourceVideoUrl, setSourceVideoUrl] = useState("");

  const [jobStatus, setJobStatus] = useState(null);
  const [error, setError] = useState("");
  const [isTranslating, setIsTranslating] = useState(false);

  async function handleProcessVideo(youtubeUrl) {
    try {
      setSourceVideoUrl(youtubeUrl);
      setError("");
      setStudyKit(null);
      setEnglishStudyKit(null);
      setSelectedLanguage("English");
      setJobId(null);

      const initialStatus = {
        status: "queued",
        progress: 0,
        message: "Starting video processing",
        error: null,
        can_continue_with_transcript: false,
      };

      setJobStatus(initialStatus);

      const response = await processVideo(youtubeUrl);
      const newJobId = response.job_id;

      setJobId(newJobId);

      setJobStatus({
        status: response.status || "queued",
        progress: 0,
        message: response.message || "Video processing started",
        error: null,
        can_continue_with_transcript: false,
      });

      pollJobStatus(newJobId);
    } catch (err) {
      const failedStatus = {
        status: "failed",
        progress: 100,
        message: "Processing failed",
        error: err.message || "Failed to process video",
        can_continue_with_transcript: false,
      };

      setJobStatus(failedStatus);
      setError(err.message || "Failed to process video");
    }
  }

  async function pollJobStatus(newJobId) {
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

          const kit = await getStudyKit(newJobId);

          setJobId(newJobId);
          setEnglishStudyKit(kit);
          setStudyKit(kit);
          setSelectedLanguage("English");

          setJobStatus({
            status: "completed",
            progress: 100,
            message: "Study kit ready",
            error: null,
            can_continue_with_transcript: false,
          });
        }

        if (job.status === "failed") {
          clearInterval(intervalId);
          setError(job.error || "Processing failed");
        }

        if (attempts >= maxAttempts) {
          clearInterval(intervalId);

          const timeoutMessage =
            "Processing took too long. Please try a shorter lecture.";

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

  async function handleLanguageChange(language) {
    setSelectedLanguage(language);

    if (!englishStudyKit || !jobId) {
      return;
    }

    if (language === "English") {
      setStudyKit(englishStudyKit);
      return;
    }

    try {
      setIsTranslating(true);
      setError("");

      const translatedKit = await translateStudyKit(jobId, language);

      setStudyKit(translatedKit);
    } catch (err) {
      setError(err.message || "Translation failed");
    } finally {
      setIsTranslating(false);
    }
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
                Turn YouTube lectures into study kits
              </h1>

              <p className="mt-3 max-w-3xl text-base leading-7 text-slate-600">
                Paste a YouTube lecture URL. LectureForge processes the video
                once in English, then lets you translate the generated study
                material without reprocessing the video.
              </p>
            </div>

            <VideoForm
              onSubmit={handleProcessVideo}
              disabled={isProcessing || isTranslating}
            />
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

        {studyKit && (
          <StudyDashboard
            studyKit={studyKit}
            jobId={jobId}
            sourceVideoUrl={sourceVideoUrl}
            selectedLanguage={selectedLanguage}
            onLanguageChange={handleLanguageChange}
            isTranslating={isTranslating}
          />
        )}
      </main>
    </div>
  );
}