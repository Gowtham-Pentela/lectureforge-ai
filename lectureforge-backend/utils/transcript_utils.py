import re
from typing import List
from models.schemas import TranscriptChunk


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = text.replace("[Music]", "")
    text = text.replace("[Applause]", "")
    return text.strip()


def format_timestamp(seconds: float) -> str:
    try:
        seconds = int(float(seconds))
    except Exception:
        seconds = 0

    if seconds < 0:
        seconds = 0

    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hrs:02d}:{mins:02d}:{secs:02d}"


def youtube_timestamp_url(youtube_url: str, seconds: float) -> str:
    try:
        seconds = int(float(seconds))
    except Exception:
        seconds = 0

    if seconds < 0:
        seconds = 0

    separator = "&" if "?" in youtube_url else "?"
    return f"{youtube_url}{separator}t={seconds}s"


def merge_small_chunks(
    chunks: List[TranscriptChunk],
    max_chars: int = 1200,
) -> List[TranscriptChunk]:
    merged = []
    current_text = ""
    current_start = None
    current_end = None

    for chunk in chunks:
        if current_start is None:
            current_start = chunk.start

        if len(current_text) + len(chunk.text) <= max_chars:
            current_text += " " + chunk.text
            current_end = chunk.end
        else:
            merged.append(
                TranscriptChunk(
                    start=current_start,
                    end=current_end,
                    start_time=format_timestamp(current_start),
                    end_time=format_timestamp(current_end),
                    text=clean_text(current_text),
                )
            )
            current_text = chunk.text
            current_start = chunk.start
            current_end = chunk.end

    if current_text:
        merged.append(
            TranscriptChunk(
                start=current_start,
                end=current_end,
                start_time=format_timestamp(current_start),
                end_time=format_timestamp(current_end),
                text=clean_text(current_text),
            )
        )

    return merged


def transcript_to_plain_text(chunks: List[TranscriptChunk]) -> str:
    lines = []
    for chunk in chunks:
        lines.append(
            f"[{format_timestamp(chunk.start)} - {format_timestamp(chunk.end)}] {chunk.text}"
        )
    return "\n".join(lines)


def plain_text_to_chunks(
    transcript: str,
    chunk_chars: int = 1000,
    seconds_per_chunk: int = 60,
) -> List[TranscriptChunk]:
    transcript = clean_text(transcript)

    if not transcript:
        return []

    words = transcript.split()
    chunks = []
    current_words = []
    current_len = 0
    start = 0.0

    for word in words:
        current_words.append(word)
        current_len += len(word) + 1

        if current_len >= chunk_chars:
            end = start + seconds_per_chunk
            chunks.append(
                TranscriptChunk(
                    start=start,
                    end=end,
                    start_time=format_timestamp(start),
                    end_time=format_timestamp(end),
                    text=" ".join(current_words),
                )
            )
            current_words = []
            current_len = 0
            start = end

    if current_words:
        end = start + seconds_per_chunk
        chunks.append(
            TranscriptChunk(
                start=start,
                end=end,
                start_time=format_timestamp(start),
                end_time=format_timestamp(end),
                text=" ".join(current_words),
            )
        )

    return chunks