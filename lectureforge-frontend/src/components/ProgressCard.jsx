import React, { useState } from "react";
import { AlertTriangle, CheckCircle2, FileText, Loader2 } from "lucide-react";

export default function ProgressCard({ status, onSubmitTranscript }) {
  const [lectureTitle, setLectureTitle] = useState("");
  const [transcript, setTranscript] = useState("");

  if (!status) return null;

  const isFailed = status.status === "failed";
  const isCompleted = status.status === "completed";
  const failureHint = getFailureHint(status);
  const canPasteTranscript =
    isFailed && status.can_continue_with_transcript && onSubmitTranscript;
  const title = isCompleted
    ? "Study kit ready"
    : isFailed
    ? "Processing failed"
    : "Processing your lecture";
  const statusMessage = isFailed
    ? canPasteTranscript
      ? "The URL path did not complete, but you can continue with a pasted transcript."
      : "The URL path did not complete. Review the detail below and retry when ready."
    : status.message || "Processing your video. This can take a moment.";

  return (
    <section className="mx-auto grid min-h-[calc(100vh-9rem)] max-w-4xl place-items-center px-4 py-12 text-center">
      <div className="w-full rounded-[2rem] border border-[var(--app-border)] bg-white/90 px-6 py-10 shadow-[0_28px_90px_rgba(0,0,0,0.10)] sm:px-10">
        <div
          className={`mx-auto grid h-20 w-20 place-items-center rounded-3xl ${
            isFailed
              ? "bg-red-50 text-red-600"
              : isCompleted
              ? "bg-emerald-50 text-emerald-600"
              : "bg-[var(--app-accent-soft)] text-[var(--app-accent)]"
          }`}
        >
          {isFailed ? (
            <AlertTriangle size={34} />
          ) : isCompleted ? (
            <CheckCircle2 size={34} />
          ) : (
            <Loader2 size={38} className="animate-spin" />
          )}
        </div>

        <h2 className="mt-6 text-4xl font-black tracking-[-0.04em] text-black sm:text-5xl">
          {title}
        </h2>

        <p className="mx-auto mt-4 max-w-2xl text-lg font-semibold leading-8 text-[var(--app-muted)]">
          {statusMessage}
        </p>

        {!isFailed && (
          <div className="mx-auto mt-8 max-w-xl">
            <div className="h-3 overflow-hidden rounded-full bg-[var(--app-red-soft)]">
              <div
                className="h-full rounded-full bg-[var(--app-accent)] transition-all duration-500"
                style={{ width: `${status.progress || 0}%` }}
              />
            </div>
            <div className="mt-3 font-mono text-sm font-bold text-[var(--app-muted)]">
              {status.progress || 0}% complete
            </div>
          </div>
        )}

        {isFailed && status.error && (
          <div className="mx-auto mt-6 max-w-2xl rounded-2xl border border-red-100 bg-red-50 p-4 text-sm leading-6 text-red-700">
            <p className="font-semibold">{status.error}</p>
            {failureHint && (
              <p className="mt-1 text-red-600">
                {failureHint}
              </p>
            )}
          </div>
        )}

        {canPasteTranscript && (
          <form
            className="mx-auto mt-6 max-w-2xl text-left"
            onSubmit={(event) => {
              event.preventDefault();

              if (!transcript.trim()) {
                return;
              }

              onSubmitTranscript({
                lectureTitle: lectureTitle.trim(),
                transcript: transcript.trim(),
              });
            }}
          >
            <div className="mb-3 flex items-center gap-2 text-sm font-black uppercase tracking-wide text-[var(--app-muted)]">
              <FileText className="h-4 w-4" />
              Transcript fallback
            </div>

            <input
              type="text"
              value={lectureTitle}
              onChange={(event) => setLectureTitle(event.target.value)}
              placeholder="Lecture title optional"
              className="mb-3 w-full rounded-xl border border-[var(--app-border)] bg-white px-4 py-3 text-sm font-semibold text-[var(--app-text)] outline-none focus:border-[var(--app-accent)]"
            />

            <textarea
              value={transcript}
              onChange={(event) => setTranscript(event.target.value)}
              placeholder="Paste the YouTube transcript here to generate the same study kit without re-reading the video URL."
              className="min-h-36 w-full resize-y rounded-xl border border-[var(--app-border)] bg-white px-4 py-3 text-sm leading-6 text-[var(--app-text)] outline-none focus:border-[var(--app-accent)]"
            />

            <button
              type="submit"
              disabled={!transcript.trim()}
              className="mt-3 inline-flex min-h-11 items-center justify-center rounded-xl bg-[var(--app-accent)] px-5 text-sm font-black text-white transition hover:bg-[var(--app-accent-strong)] disabled:cursor-not-allowed disabled:bg-[var(--app-soft)]"
            >
              Generate from transcript
            </button>
          </form>
        )}
      </div>
    </section>
  );
}

function getFailureHint(status) {
  if (!status) {
    return "";
  }

  if (status.error_code === "SERVERLESS_AUDIO_TRANSCRIPTION_UNAVAILABLE") {
    return "No-caption videos need a longer-running backend worker. Captioned videos should still process quickly.";
  }

  if (status.error_code === "OPENAI_TRANSCRIPTION_ERROR") {
    return "The hosted backend could not complete audio transcription for this video.";
  }

  if (status.error_code === "OPENAI_AUDIO_TOO_LARGE") {
    return "No-caption videos over the upload limit need chunked background transcription.";
  }

  if (status.error_code === "OPENAI_QUOTA_ERROR") {
    return "Check OpenAI billing and quota on the backend API key.";
  }

  if (status.error_code === "OPENAI_AUTH_ERROR") {
    return "Check the backend OPENAI_API_KEY configured in Render.";
  }

  if (status.error_code === "OPENAI_RATE_LIMIT") {
    return "The backend will avoid audio transcription when captions or transcript services are available.";
  }

  if (status.can_continue_with_transcript) {
    return "Paste the lecture transcript below to keep building the study kit.";
  }

  return "";
}
