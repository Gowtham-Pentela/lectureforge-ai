from typing import List, Optional
from pydantic import BaseModel


class TranscriptChunk(BaseModel):
    start: float
    end: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    text: str


class OutlineItem(BaseModel):
    title: str
    start: float
    end: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    summary: str


class KeyConcept(BaseModel):
    concept: str
    explanation: str
    timestamp: float
    timestamp_time: Optional[str] = None


class Summaries(BaseModel):
    short_summary: str
    medium_summary: str
    full_summary: str


# Backward-compatible name used by agents/agent3_study.py
class SummarySet(Summaries):
    pass


class Flashcard(BaseModel):
    question: str
    answer: str
    timestamp: float
    timestamp_time: Optional[str] = None


class ConceptMapNode(BaseModel):
    id: str
    label: str
    type: Optional[str] = "concept"


class ConceptMapEdge(BaseModel):
    source: str
    target: str
    label: Optional[str] = None


class ConceptMap(BaseModel):
    nodes: List[ConceptMapNode]
    edges: List[ConceptMapEdge]


class LectureAnalysis(BaseModel):
    title: str
    outline: List[OutlineItem]
    key_concepts: List[KeyConcept]


class StudyKit(BaseModel):
    lecture_title: str
    duration_seconds: Optional[float] = None
    duration_time: Optional[str] = None
    transcript_chunks: List[TranscriptChunk]
    outline: List[OutlineItem]
    key_concepts: List[KeyConcept]
    summaries: SummarySet
    flashcards: List[Flashcard]
    concept_map: ConceptMap
    bilingual_output: Optional[dict] = None


class ProcessVideoRequest(BaseModel):
    youtube_url: str
    target_language: Optional[str] = "English"


class ProcessTranscriptRequest(BaseModel):
    lecture_title: str
    transcript: str
    target_language: Optional[str] = "English"


class ProcessVideoResponse(BaseModel):
    job_id: str
    status: str
    message: str


class TranslateStudyKitRequest(BaseModel):
    job_id: str
    target_language: str


class SearchRequest(BaseModel):
    job_id: str
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    text: str
    start: float
    end: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]