const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function parseResponse(response) {
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.detail ||
      data?.error ||
      "Request failed";
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }

  return data;
}

export async function processVideo({ youtubeUrl, targetLanguage }) {
  const response = await fetch(`${API_BASE_URL}/process-video`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      youtube_url: youtubeUrl,
      target_language: targetLanguage || "English",
    }),
  });

  return parseResponse(response);
}

export async function getJobStatus(jobId) {
  const response = await fetch(`${API_BASE_URL}/job-status/${jobId}`);
  return parseResponse(response);
}

export async function getStudyKit(jobId) {
  const response = await fetch(`${API_BASE_URL}/study-kit/${jobId}`);
  return parseResponse(response);
}

export async function searchStudyKit({ jobId, query, topK = 5 }) {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job_id: jobId,
      query,
      top_k: topK,
    }),
  });

  return parseResponse(response);
}
