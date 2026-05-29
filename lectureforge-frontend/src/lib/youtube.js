export function buildYouTubeJumpUrl(url, startSeconds = 0) {
  if (!url) {
    return "";
  }

  try {
    const parsedUrl = new URL(url);

    parsedUrl.searchParams.delete("t");
    parsedUrl.searchParams.delete("start");

    if (
      parsedUrl.hostname.includes("youtu.be") ||
      parsedUrl.hostname.includes("youtube.com")
    ) {
      parsedUrl.searchParams.set("t", `${Math.max(0, startSeconds)}s`);
      return parsedUrl.toString();
    }

    return "";
  } catch {
    return "";
  }
}

export function buildYouTubeEmbedUrl(url, startSeconds = 0) {
  const videoId = getYouTubeVideoId(url);

  if (!videoId) {
    return "";
  }

  const params = new URLSearchParams({
    rel: "0",
    modestbranding: "1",
  });

  if (startSeconds > 0) {
    params.set("start", String(Math.floor(startSeconds)));
  }

  return `https://www.youtube.com/embed/${videoId}?${params.toString()}`;
}

export function getYouTubeVideoId(url) {
  if (!url) {
    return "";
  }

  try {
    const parsedUrl = new URL(url);

    if (parsedUrl.hostname.includes("youtu.be")) {
      return parsedUrl.pathname.replace("/", "");
    }

    if (parsedUrl.hostname.includes("youtube.com")) {
      return parsedUrl.searchParams.get("v") || "";
    }

    return "";
  } catch {
    return "";
  }
}

export function formatTime(seconds) {
  if (
    seconds === null ||
    seconds === undefined ||
    Number.isNaN(Number(seconds))
  ) {
    return "00:00";
  }

  const totalSeconds = Math.floor(Number(seconds));
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const secs = totalSeconds % 60;
  const parts = hours > 0 ? [hours, minutes, secs] : [minutes, secs];

  return parts.map((value) => String(value).padStart(2, "0")).join(":");
}
