const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function processVideo(youtubeUrl) {
  const response = await fetch(`${API_BASE_URL}/process-video`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      youtube_url: youtubeUrl,
      target_language: "English",
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to process video");
  }

  return response.json();
}

export async function getJobStatus(jobId) {
  const response = await fetch(`${API_BASE_URL}/job-status/${jobId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get job status");
  }

  return response.json();
}

export async function getStudyKit(jobId) {
  const response = await fetch(`${API_BASE_URL}/study-kit/${jobId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(
      error.detail?.message || error.detail || "Failed to get study kit"
    );
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
      error.detail?.message ||
        error.detail ||
        "Failed to translate study kit"
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
    throw new Error(error.detail || "Search failed");
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
      error.detail?.message ||
        error.detail ||
        `Failed to translate ${section}`
    );
  }

  return response.json();
}