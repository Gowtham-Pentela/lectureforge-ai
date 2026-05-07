from typing import Optional
from models.schemas import StudyKit
from utils.transcript_utils import format_timestamp


def clamp_timestamp(value: Optional[float], min_time: float, max_time: float) -> float:
    try:
        value = float(value)
    except Exception:
        return min_time

    if value < min_time:
        return min_time

    if value > max_time:
        return max_time

    return value


def find_best_timestamp_for_text(study_kit: StudyKit, text: str) -> float:
    if not text or not study_kit.transcript_chunks:
        return study_kit.transcript_chunks[0].start if study_kit.transcript_chunks else 0.0

    text_lower = text.lower()
    best_score = 0
    best_time = study_kit.transcript_chunks[0].start

    keywords = [
        word.strip(".,!?;:()[]{}\"'").lower()
        for word in text_lower.split()
        if len(word.strip(".,!?;:()[]{}\"'")) >= 5
    ]

    for chunk in study_kit.transcript_chunks:
        chunk_text = chunk.text.lower()
        score = sum(1 for word in keywords if word in chunk_text)

        if score > best_score:
            best_score = score
            best_time = chunk.start

    return best_time


def validate_study_kit(study_kit: StudyKit) -> StudyKit:
    if not study_kit.transcript_chunks:
        return study_kit

    min_time = min(chunk.start for chunk in study_kit.transcript_chunks)
    max_time = max(chunk.end for chunk in study_kit.transcript_chunks)

    study_kit.duration_seconds = max_time
    study_kit.duration_time = format_timestamp(max_time)

    for chunk in study_kit.transcript_chunks:
        chunk.start = clamp_timestamp(chunk.start, min_time, max_time)
        chunk.end = clamp_timestamp(chunk.end, min_time, max_time)

        if chunk.end < chunk.start:
            chunk.end = chunk.start

        chunk.start_time = format_timestamp(chunk.start)
        chunk.end_time = format_timestamp(chunk.end)

    for item in study_kit.outline:
        item.start = clamp_timestamp(item.start, min_time, max_time)
        item.end = clamp_timestamp(item.end, min_time, max_time)

        if item.end < item.start:
            item.end = item.start

        item.start_time = format_timestamp(item.start)
        item.end_time = format_timestamp(item.end)

    for concept in study_kit.key_concepts:
        concept.timestamp = clamp_timestamp(concept.timestamp, min_time, max_time)
        concept.timestamp_time = format_timestamp(concept.timestamp)

    for card in study_kit.flashcards:
        card.timestamp = clamp_timestamp(card.timestamp, min_time, max_time)
        card.timestamp_time = format_timestamp(card.timestamp)

    return study_kit