from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ProcessVideoRequest(BaseModel):
    youtube_url: str
    target_language: Optional[str] = "English"


class ProcessTranscriptRequest(BaseModel):
    lecture_title: Optional[str] = "Untitled Lecture"
    transcript: str
    target_language: Optional[str] = "English"


class ProcessVideoResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str


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


class LectureAnalysis(BaseModel):
    title: str
    outline: List[OutlineItem]
    key_concepts: List[KeyConcept]


class SummarySet(BaseModel):
    short_summary: str
    medium_summary: str
    full_summary: str


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
    label: str


class ConceptMap(BaseModel):
    nodes: List[ConceptMapNode]
    edges: List[ConceptMapEdge]


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
    bilingual_output: Optional[Dict[str, Any]] = None


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