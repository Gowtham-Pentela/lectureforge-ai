from typing import List, Optional
from pydantic import BaseModel, Field


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
    timestamp: Optional[float] = None


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
    user_id: Optional[str] = None


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


class TranslateSectionRequest(BaseModel):
    job_id: str
    target_language: str
    section: str
    batch_start: Optional[int] = 0
    batch_size: Optional[int] = 5


class SearchRequest(BaseModel):
    job_id: str
    query: str
    top_k: int = 5
    target_language: Optional[str] = "English"


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


class LiveAgentRequest(BaseModel):
    job_id: str
    message: str
    active_tab: Optional[str] = "outline"
    target_language: Optional[str] = "English"
    screen_shared: bool = False
    voice_enabled: bool = False


class LiveAgentResponse(BaseModel):
    reply: str
    context_cards: List[str] = Field(default_factory=list)


class FacultyAuditRequest(BaseModel):
    youtube_url: str


class FacultyAuditFromStudyKitRequest(BaseModel):
    job_id: str


class HighestImpactFix(BaseModel):
    timestamp: str
    issue: str
    why_it_matters: str
    suggested_improvement: str


class PriorityFix(BaseModel):
    priority: str
    timestamp: str
    issue: str
    why_it_matters: str
    suggested_improvement: str


class AuditDimension(BaseModel):
    summary: str
    strengths: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)


class TimestampedRewrite(BaseModel):
    timestamp: str
    current_issue: str
    suggested_rewrite: str
    why_this_helps: str


class FacultyAuditReport(BaseModel):
    lecture_title: Optional[str] = None
    overall_summary: str
    highest_impact_fix: HighestImpactFix
    priority_fixes: List[PriorityFix]
    pedagogical_clarity: AuditDimension
    accessibility: AuditDimension
    equity_and_inclusion: AuditDimension
    structure_and_pacing: AuditDimension
    cognitive_load: AuditDimension
    student_engagement: AuditDimension
    timestamped_rewrites: List[TimestampedRewrite]
    final_notes: str
