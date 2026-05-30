const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function getErrorMessage(error, fallback) {
  return (
    error?.detail?.message ||
    error?.detail ||
    error?.message ||
    fallback
  );
}

function getLectureForgeUserId() {
  const storageKey = "lectureforge_user_id";
  const existingId = localStorage.getItem(storageKey);

  if (existingId) {
    return existingId;
  }

  const nextId =
    typeof crypto !== "undefined" && crypto.randomUUID
      ? crypto.randomUUID()
      : `user_${Date.now()}_${Math.random().toString(16).slice(2)}`;

  localStorage.setItem(storageKey, nextId);
  return nextId;
}

export async function processVideo(youtubeUrl) {
  const response = await fetch(`${API_BASE_URL}/process-video`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      youtube_url: youtubeUrl,
      target_language: "English",
      user_id: getLectureForgeUserId(),
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(getErrorMessage(error, "Failed to process video"));
  }

  return response.json();
}

export async function processTranscript({ lectureTitle, transcript }) {
  const response = await fetch(`${API_BASE_URL}/process-transcript`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      lecture_title: lectureTitle || "Pasted lecture transcript",
      transcript,
      target_language: "English",
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(getErrorMessage(error, "Failed to process transcript"));
  }

  return response.json();
}

export async function getJobStatus(jobId) {
  const response = await fetch(`${API_BASE_URL}/job-status/${jobId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(getErrorMessage(error, "Failed to get job status"));
  }

  return response.json();
}

export async function getStudyKit(jobId) {
  const response = await fetch(`${API_BASE_URL}/study-kit/${jobId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(getErrorMessage(error, "Failed to get study kit"));
  }

  return response.json();
}

export async function translateStudyKit(jobId, targetLanguage) {
  const response = await fetch(`${API_BASE_URL}/translate-study-kit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job_id: jobId,
      target_language: targetLanguage,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(
      getErrorMessage(error, "Failed to translate study kit")
    );
  }

  return response.json();
}

export async function searchStudyKit(
  jobId,
  query,
  topK = 5,
  targetLanguage = "English"
) {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job_id: jobId,
      query,
      top_k: topK,
      target_language: targetLanguage,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(getErrorMessage(error, "Search failed"));
  }

  return response.json();
}

export async function askLiveAgent({
  jobId,
  message,
  activeTab = "outline",
  targetLanguage = "English",
  screenShared = false,
  voiceEnabled = false,
}) {
  const response = await fetch(`${API_BASE_URL}/live-agent`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job_id: jobId,
      message,
      active_tab: activeTab,
      target_language: targetLanguage,
      screen_shared: screenShared,
      voice_enabled: voiceEnabled,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(getErrorMessage(error, "Live agent failed"));
  }

  return response.json();
}

export async function translateSection({
  jobId,
  targetLanguage,
  section,
  batchStart = 0,
  batchSize = 5,
}) {
  const response = await fetch(`${API_BASE_URL}/translate-section`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job_id: jobId,
      target_language: targetLanguage,
      section,
      batch_start: batchStart,
      batch_size: batchSize,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(
      getErrorMessage(error, `Failed to translate ${section}`)
    );
  }

  return response.json();
}
