import React, { useEffect, useRef, useState } from "react";
import Header from "./components/Header";
import VideoForm from "./components/VideoForm";
import ProgressCard from "./components/ProgressCard";
import StudyDashboard from "./components/StudyDashboard";
import { getJobStatus, getStudyKit, processVideo } from "./lib/api";

export default function App() {
  const [youtubeUrl, setYoutubeUrl] = useState("https://www.youtube.com/watch?v=aircAruvnKk");
  const [targetLanguage, setTargetLanguage] = useState("English");
  const [jobId, setJobId] = useState("");
  const [jobStatus, setJobStatus] = useState(null);
  const [studyKit, setStudyKit] = useState(null);
  const [error, setError] = useState("");
  const [isStarting, setIsStarting] = useState(false);
  const pollRef = useRef(null);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setStudyKit(null);
    setJobStatus(null);
    setJobId("");
    setIsStarting(true);

    try {
      const data = await processVideo({
        youtubeUrl,
        targetLanguage,
      });

      setJobId(data.job_id);
      setJobStatus({
        job_id: data.job_id,
        status: data.status,
        progress: 0,
        message: data.message,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsStarting(false);
    }
  }

  useEffect(() => {
    if (!jobId) return;

    if (pollRef.current) {
      clearInterval(pollRef.current);
    }

    pollRef.current = setInterval(async () => {
      try {
        const status = await getJobStatus(jobId);
        setJobStatus(status);

        if (status.status === "completed") {
          clearInterval(pollRef.current);
          pollRef.current = null;

          const kit = await getStudyKit(jobId);
          setStudyKit(kit);
        }

        if (status.status === "failed") {
          clearInterval(pollRef.current);
          pollRef.current = null;
        }
      } catch (err) {
        setError(err.message);
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    }, 1800);

    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [jobId]);

  const isLoading =
    isStarting ||
    (jobStatus &&
      jobStatus.status !== "completed" &&
      jobStatus.status !== "failed");

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-6 md:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <Header />

        <VideoForm
          youtubeUrl={youtubeUrl}
          setYoutubeUrl={setYoutubeUrl}
          targetLanguage={targetLanguage}
          setTargetLanguage={setTargetLanguage}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />

        {error && (
          <div className="mt-5 rounded-3xl border border-red-100 bg-red-50 p-5 text-sm font-semibold leading-6 text-red-700">
            {error}
          </div>
        )}

        <div className="mt-5">
          <ProgressCard status={jobStatus} />
        </div>

        {studyKit && <StudyDashboard jobId={jobId} studyKit={studyKit} />}
      </div>
    </div>
  );
}
