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

  const [status, setStatus] = useState("idle");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [isTranslating, setIsTranslating] = useState(false);

  async function handleProcessVideo(youtubeUrl) {
    try {
      setError("");
      setStudyKit(null);
      setEnglishStudyKit(null);
      setSelectedLanguage("English");
      setJobId(null);
      setStatus("queued");
      setProgress(0);
      setMessage("Starting video processing");

      const response = await processVideo(youtubeUrl);
      const newJobId = response.job_id;

      setJobId(newJobId);
      setStatus(response.status);
      setMessage(response.message || "Video processing started");

      pollJobStatus(newJobId);
    } catch (err) {
      setStatus("failed");
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

        setStatus(job.status);
        setProgress(job.progress || 0);
        setMessage(job.message || "");

        if (job.status === "completed") {
          clearInterval(intervalId);

          const kit = await getStudyKit(newJobId);

          setJobId(newJobId);
          setEnglishStudyKit(kit);
          setStudyKit(kit);
          setSelectedLanguage("English");
          setProgress(100);
          setMessage("Study kit ready");
          setStatus("completed");
        }

        if (job.status === "failed") {
          clearInterval(intervalId);
          setStatus("failed");
          setError(job.error || "Processing failed");
        }

        if (attempts >= maxAttempts) {
          clearInterval(intervalId);
          setStatus("failed");
          setError("Processing took too long. Please try a shorter lecture.");
        }
      } catch (err) {
        clearInterval(intervalId);
        setStatus("failed");
        setError(err.message || "Failed to check job status");
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
              disabled={status === "processing" || status === "queued"}
            />
          </div>
        </section>

        {(status === "queued" || status === "processing") && (
          <ProgressCard
            status={status}
            progress={progress}
            message={message}
          />
        )}

        {error && (
          <div className="mb-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {studyKit && (
          <StudyDashboard
            studyKit={studyKit}
            jobId={jobId}
            selectedLanguage={selectedLanguage}
            onLanguageChange={handleLanguageChange}
            isTranslating={isTranslating}
          />
        )}
      </main>
    </div>
  );
}