import os
import uuid
import json
import asyncio
import numpy as np
from copy import deepcopy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    ProcessVideoRequest,
    ProcessTranscriptRequest,
    ProcessVideoResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    LiveAgentRequest,
    LiveAgentResponse,
    LectureAnalysis,
    StudyKit,
    SummarySet,
    ConceptMap,
    TranslateStudyKitRequest,
    TranslateSectionRequest,
    FacultyAuditRequest,
    FacultyAuditFromStudyKitRequest,
    FacultyAuditReport,
    TranscriptChunk,
)

from services.job_store import JobStore
from services.video_cache import VideoCache
from services.openai_service import create_embedding, generate_text, generate_json
from agents.agent1_ingestion import Agent1Ingestion
from agents.agent2_analysis import Agent2Analysis
from agents.agent3_study import Agent3Study
from agents.agent4_faculty_audit import generate_faculty_audit
from utils.transcript_utils import (
    plain_text_to_chunks,
    format_timestamp,
    transcript_to_plain_text,
)
from utils.study_kit_validator import validate_study_kit
from utils.faculty_audit_validator import validate_faculty_audit


app = FastAPI(
    title="LectureForge AI Backend",
    description="AI backend for turning YouTube lectures into student study kits",
    version="0.2.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv("LECTUREFORGE_CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials="*" not in cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


job_store = JobStore()
video_cache = VideoCache()

agent1 = Agent1Ingestion()
agent2 = Agent2Analysis()
agent3 = Agent3Study()


@app.get("/")
def root():
    return {
        "app": "LectureForge AI Backend",
        "status": "running",
        "docs": "/docs",
        "capabilities": [
            "student_study_kit",
        ],
    }


if os.getenv("LECTUREFORGE_ENABLE_DEBUG_ENDPOINTS") == "true":
    @app.get("/debug-env")
    def debug_env():
        openai_key = os.getenv("OPENAI_API_KEY")
        supadata_key = os.getenv("SUPADATA_API_KEY")

        return {
            "openai_key_present": bool(openai_key),
            "openai_key_prefix": openai_key[:7] if openai_key else None,
            "openai_key_length": len(openai_key) if openai_key else 0,
            "openai_model": os.getenv("OPENAI_MODEL"),
            "embedding_model": os.getenv("OPENAI_EMBEDDING_MODEL"),
            "supadata_key_present": bool(supadata_key),
            "supadata_key_prefix": supadata_key[:7] if supadata_key else None,
            "supadata_key_length": len(supadata_key) if supadata_key else 0,
        }


    @app.get("/debug-openai")
    def debug_openai():
        try:
            result = generate_text(
                system_prompt="You are a test assistant.",
                user_prompt="Reply with exactly: OpenAI connection works",
            )

            return {
                "success": True,
                "response": result,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


@app.post("/process-video", response_model=ProcessVideoResponse)
async def process_video(request: ProcessVideoRequest):
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id)
    youtube_video_id = extract_youtube_video_id_safe(request.youtube_url)
    cached_study_kit = video_cache.get_completed_study_kit(
        youtube_video_id=youtube_video_id,
        user_id=request.user_id,
    )

    if cached_study_kit:
        study_kit = StudyKit(**cached_study_kit)
        study_kit = validate_study_kit(study_kit)
        job_store.update_job(
            job_id,
            status="completed",
            progress=100,
            message="Study kit loaded from cache",
            study_kit=study_kit,
            embeddings=[],
            search_index_status="queued",
            ready_sections=[
                "transcript",
                "outline",
                "summaries",
                "concept_map",
                "flashcards",
            ],
            user_id=request.user_id,
            youtube_url=request.youtube_url,
            youtube_video_id=youtube_video_id,
        )

        return ProcessVideoResponse(
            job_id=job_id,
            status="completed",
            message="Study kit loaded from cache",
        )

    job_store.update_job(
        job_id,
        user_id=request.user_id,
        youtube_url=request.youtube_url,
        youtube_video_id=youtube_video_id,
    )

    asyncio.create_task(
        run_video_processing_pipeline(
            job_id=job_id,
            youtube_url=request.youtube_url,
            target_language="English",
            user_id=request.user_id,
            youtube_video_id=youtube_video_id,
        )
    )

    return ProcessVideoResponse(
        job_id=job_id,
        status="queued",
        message="Video processing started",
    )


@app.post("/process-transcript", response_model=ProcessVideoResponse)
async def process_transcript(request: ProcessTranscriptRequest):
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id)

    asyncio.create_task(
        run_transcript_processing_pipeline(
            job_id=job_id,
            lecture_title=request.lecture_title,
            transcript=request.transcript,
            target_language="English",
        )
    )

    return ProcessVideoResponse(
        job_id=job_id,
        status="queued",
        message="Transcript processing started",
    )


@app.post("/process-faculty-audit", response_model=ProcessVideoResponse)
async def process_faculty_audit(request: FacultyAuditRequest):
    job_id = str(uuid.uuid4())
    job_store.create_job(job_id)

    asyncio.create_task(
        run_faculty_audit_pipeline(
            job_id=job_id,
            youtube_url=request.youtube_url,
        )
    )

    return ProcessVideoResponse(
        job_id=job_id,
        status="queued",
        message="Faculty audit started",
    )


@app.post("/process-faculty-audit-from-study-kit", response_model=ProcessVideoResponse)
async def process_faculty_audit_from_study_kit(
    request: FacultyAuditFromStudyKitRequest,
):
    source_job = job_store.get_job(request.job_id)

    if not source_job:
        raise HTTPException(status_code=404, detail="Study kit job not found")

    if source_job.get("status") != "completed" or not source_job.get("study_kit"):
        raise HTTPException(status_code=400, detail="Study kit is not ready yet")

    job_id = str(uuid.uuid4())
    job_store.create_job(job_id)

    asyncio.create_task(
        run_faculty_audit_from_study_kit_pipeline(
            job_id=job_id,
            source_job_id=request.job_id,
        )
    )

    return ProcessVideoResponse(
        job_id=job_id,
        status="queued",
        message="Faculty audit started from generated study kit",
    )


async def run_video_processing_pipeline(
    job_id: str,
    youtube_url: str,
    target_language: str,
    user_id: str = None,
    youtube_video_id: str = None,
):
    try:
        job_store.update_job(
            job_id,
            status="processing",
            progress=10,
            message="Agent 1 is extracting transcript from YouTube",
        )

        transcript_chunks = await asyncio.to_thread(
            agent1.get_transcript,
            youtube_url,
        )

        study_kit = await run_common_study_pipeline(
            job_id=job_id,
            transcript_chunks=transcript_chunks,
            target_language=target_language,
            lecture_title_override=None,
        )

        video_cache.save_completed_study_kit(
            youtube_video_id=youtube_video_id,
            youtube_url=youtube_url,
            study_kit=study_kit,
            user_id=user_id,
            transcript_provider=os.getenv("LECTUREFORGE_TRANSCRIPT_PROVIDER", "auto"),
        )

    except Exception as e:
        public_error = build_public_error_message(str(e))

        job_store.update_job(
            job_id,
            status="failed",
            progress=100,
            message="Processing failed",
            error=public_error["message"],
            raw_error=public_error.get("raw_error"),
            error_code=public_error["error_code"],
            can_continue_with_transcript=public_error["can_continue_with_transcript"],
        )


async def run_faculty_audit_pipeline(job_id: str, youtube_url: str):
    try:
        job_store.update_job(
            job_id,
            status="processing",
            progress=10,
            message="Agent 1 is extracting transcript for faculty audit",
        )

        transcript_chunks = await asyncio.to_thread(
            agent1.get_transcript,
            youtube_url,
        )

        if not transcript_chunks:
            raise ValueError("No transcript chunks available for faculty audit")

        job_store.update_job(
            job_id,
            status="processing",
            progress=25,
            message="Normalizing transcript to English for faculty audit",
        )

        transcript_chunks = await asyncio.to_thread(
            normalize_transcript_chunks_to_english,
            transcript_chunks,
        )

        job_store.update_job(
            job_id,
            status="processing",
            progress=35,
            message=f"Transcript ready with {len(transcript_chunks)} chunks. Agent 2 is identifying lecture title and structure",
        )

        analysis = await asyncio.to_thread(
            agent2.analyze,
            transcript_chunks,
        )

        lecture_title = (
            analysis.title
            if analysis and getattr(analysis, "title", None)
            else "Untitled Lecture"
        )

        job_store.update_job(
            job_id,
            status="processing",
            progress=60,
            message=f"Lecture identified: {lecture_title}. Generating private faculty audit",
        )

        faculty_audit = await asyncio.to_thread(
            generate_faculty_audit,
            transcript_chunks,
            lecture_title,
        )

        faculty_audit = validate_faculty_audit(faculty_audit)

        faculty_audit_payload = (
            faculty_audit.model_dump()
            if hasattr(faculty_audit, "model_dump")
            else faculty_audit.dict()
            if hasattr(faculty_audit, "dict")
            else faculty_audit
        )

        job_store.update_job(
            job_id,
            status="completed",
            progress=100,
            message="Faculty audit ready",
            faculty_audit=faculty_audit_payload,
        )

    except Exception as e:
        public_error = build_public_error_message(str(e))

        job_store.update_job(
            job_id,
            status="failed",
            progress=100,
            message="Faculty audit failed",
            error=public_error["message"],
            raw_error=str(e),
            error_code=public_error["error_code"],
            can_continue_with_transcript=public_error["can_continue_with_transcript"],
        )


async def run_faculty_audit_from_study_kit_pipeline(
    job_id: str,
    source_job_id: str,
):
    try:
        source_job = job_store.get_job(source_job_id)

        if not source_job or not source_job.get("study_kit"):
            raise ValueError("Completed study kit was not found")

        study_kit = source_job["study_kit"]
        lecture_title = get_study_kit_value(study_kit, "lecture_title") or "Untitled Lecture"
        transcript_chunks = get_study_kit_value(study_kit, "transcript_chunks") or []
        transcript_chunks = normalize_transcript_chunk_objects(transcript_chunks)

        if not transcript_chunks:
            raise ValueError("Study kit did not contain transcript chunks")

        job_store.update_job(
            job_id,
            status="processing",
            progress=30,
            message="Reusing generated study kit transcript for faculty review",
        )

        faculty_audit = await asyncio.to_thread(
            generate_faculty_audit,
            transcript_chunks,
            lecture_title,
        )

        faculty_audit = validate_faculty_audit(faculty_audit)

        faculty_audit_payload = (
            faculty_audit.model_dump()
            if hasattr(faculty_audit, "model_dump")
            else faculty_audit.dict()
            if hasattr(faculty_audit, "dict")
            else faculty_audit
        )

        job_store.update_job(
            job_id,
            status="completed",
            progress=100,
            message="Faculty audit ready",
            faculty_audit=faculty_audit_payload,
        )

    except Exception as e:
        public_error = build_public_error_message(str(e))

        job_store.update_job(
            job_id,
            status="failed",
            progress=100,
            message="Faculty audit failed",
            error=public_error["message"],
            raw_error=public_error.get("raw_error"),
            error_code=public_error["error_code"],
            can_continue_with_transcript=public_error["can_continue_with_transcript"],
        )


async def run_transcript_processing_pipeline(
    job_id: str,
    lecture_title: str,
    transcript: str,
    target_language: str,
):
    try:
        job_store.update_job(
            job_id,
            status="processing",
            progress=10,
            message="Converting pasted transcript into chunks",
        )

        transcript_chunks = plain_text_to_chunks(transcript)

        if not transcript_chunks:
            raise ValueError("Transcript is empty or could not be converted into chunks")

        await run_common_study_pipeline(
            job_id=job_id,
            transcript_chunks=transcript_chunks,
            target_language=target_language,
            lecture_title_override=lecture_title,
        )

    except Exception as e:
        public_error = build_public_error_message(str(e))

        job_store.update_job(
            job_id,
            status="failed",
            progress=100,
            message="Processing failed",
            error=public_error["message"],
            raw_error=public_error.get("raw_error"),
            error_code=public_error["error_code"],
            can_continue_with_transcript=public_error["can_continue_with_transcript"],
        )


async def run_common_study_pipeline(
    job_id: str,
    transcript_chunks,
    target_language: str,
    lecture_title_override=None,
):
    if not transcript_chunks:
        raise ValueError("No transcript chunks available")

    job_store.update_job(
        job_id,
        status="processing",
        progress=28,
        message="Normalizing transcript to English",
    )

    transcript_chunks = await asyncio.to_thread(
        normalize_transcript_chunks_to_english,
        transcript_chunks,
    )

    partial_study_kit = StudyKit(
        lecture_title=lecture_title_override or "Lecture transcript",
        transcript_chunks=transcript_chunks,
        outline=[],
        key_concepts=[],
        summaries=SummarySet(
            short_summary="",
            medium_summary="",
            full_summary="",
        ),
        flashcards=[],
        concept_map=ConceptMap(nodes=[], edges=[]),
        bilingual_output=None,
    )
    partial_study_kit = validate_study_kit(partial_study_kit)

    job_store.update_job(
        job_id,
        status="processing",
        progress=32,
        message="Transcript ready. Building outline",
        study_kit=partial_study_kit,
        ready_sections=["transcript"],
    )

    job_store.update_job(
        job_id,
        status="processing",
        progress=35,
        message=f"Transcript ready with {len(transcript_chunks)} chunks. Agent 2 is analyzing lecture structure",
    )

    analysis = await asyncio.to_thread(
        agent2.analyze,
        transcript_chunks,
    )

    if lecture_title_override:
        analysis = LectureAnalysis(
            title=lecture_title_override,
            outline=analysis.outline,
            key_concepts=analysis.key_concepts,
        )

    partial_study_kit.lecture_title = analysis.title
    partial_study_kit.outline = analysis.outline
    partial_study_kit.key_concepts = analysis.key_concepts
    partial_study_kit = validate_study_kit(partial_study_kit)

    job_store.update_job(
        job_id,
        status="processing",
        progress=50,
        message="Outline ready. Generating summary",
        study_kit=partial_study_kit,
        ready_sections=["transcript", "outline"],
    )

    transcript_text = transcript_to_plain_text(transcript_chunks)

    summaries = await asyncio.to_thread(
        agent3._generate_summaries,
        transcript_text,
    )

    partial_study_kit.summaries = summaries
    partial_study_kit = validate_study_kit(partial_study_kit)

    job_store.update_job(
        job_id,
        status="processing",
        progress=65,
        message="Summary ready. Building mind map",
        study_kit=partial_study_kit,
        ready_sections=["transcript", "outline", "summaries"],
    )

    concept_map = await asyncio.to_thread(
        agent3._generate_concept_map,
        transcript_text,
    )

    partial_study_kit.concept_map = concept_map
    partial_study_kit = validate_study_kit(partial_study_kit)

    job_store.update_job(
        job_id,
        status="processing",
        progress=78,
        message="Mind map ready. Creating flashcards",
        study_kit=partial_study_kit,
        ready_sections=["transcript", "outline", "summaries", "concept_map"],
    )

    flashcards = await asyncio.to_thread(
        agent3._generate_flashcards,
        transcript_text,
    )

    partial_study_kit.flashcards = flashcards
    partial_study_kit = validate_study_kit(partial_study_kit)

    job_store.update_job(
        job_id,
        status="completed",
        progress=100,
        message="Study kit ready",
        study_kit=partial_study_kit,
        embeddings=[],
        search_index_status="queued",
        ready_sections=[
            "transcript",
            "outline",
            "summaries",
            "concept_map",
            "flashcards",
        ],
    )

    asyncio.create_task(build_semantic_search_index(job_id))

    return partial_study_kit


async def build_semantic_search_index(job_id: str):
    try:
        job = job_store.get_job(job_id)

        if not job or not job.get("study_kit"):
            return

        if job.get("embeddings"):
            job_store.update_job(job_id, search_index_status="ready")
            return

        study_kit = job["study_kit"]
        transcript_chunks = get_study_kit_value(study_kit, "transcript_chunks") or []
        transcript_chunks = normalize_transcript_chunk_objects(transcript_chunks)

        if not transcript_chunks:
            job_store.update_job(
                job_id,
                search_index_status="failed",
                search_index_error="No transcript chunks found for search index",
            )
            return

        job_store.update_job(
            job_id,
            search_index_status="building",
            search_index_error="",
        )

        embeddings = await asyncio.to_thread(
            agent3.create_search_embeddings,
            transcript_chunks,
        )

        job_store.update_job(
            job_id,
            embeddings=embeddings,
            search_index_status="ready",
            search_index_error="",
        )

        video_cache.save_embeddings(
            youtube_video_id=job.get("youtube_video_id"),
            embeddings=embeddings,
        )

    except Exception as e:
        job_store.update_job(
            job_id,
            search_index_status="failed",
            search_index_error=str(e),
        )


@app.get("/job-status/{job_id}")
def get_job_status(job_id: str):
    job = job_store.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "message": job["message"],
        "error": job.get("error"),
        "raw_error": job.get("raw_error"),
        "error_code": job.get("error_code"),
        "can_continue_with_transcript": job.get("can_continue_with_transcript", False),
        "search_index_status": job.get("search_index_status", "pending"),
        "ready_sections": job.get("ready_sections", []),
        "study_kit_available": bool(job.get("study_kit")),
    }


@app.get("/study-kit/{job_id}")
def get_study_kit(job_id: str):
    job = job_store.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail={
                "message": job.get("error", "Unknown error"),
                "raw_error": job.get("raw_error"),
                "error_code": job.get("error_code"),
                "can_continue_with_transcript": job.get(
                    "can_continue_with_transcript",
                    False,
                ),
            },
        )

    if not job.get("study_kit"):
        raise HTTPException(
            status_code=202,
            detail="Study kit is not ready yet",
        )

    return job["study_kit"]


@app.get("/faculty-audit/{job_id}", response_model=FacultyAuditReport)
def get_faculty_audit(job_id: str):
    job = job_store.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail={
                "message": job.get("error", "Unknown error"),
                "raw_error": job.get("raw_error"),
                "error_code": job.get("error_code"),
                "can_continue_with_transcript": job.get(
                    "can_continue_with_transcript",
                    False,
                ),
            },
        )

    if job["status"] != "completed":
        raise HTTPException(
            status_code=202,
            detail="Faculty audit is not ready yet",
        )

    faculty_audit = job.get("faculty_audit")

    if not faculty_audit:
        raise HTTPException(
            status_code=404,
            detail="Faculty audit not found for this job",
        )

    return FacultyAuditReport(**faculty_audit) if isinstance(faculty_audit, dict) else faculty_audit

@app.post("/translate-study-kit")
def translate_study_kit(request: TranslateStudyKitRequest):
    job = job_store.get_job(request.job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Study kit is not ready yet",
        )

    target_language = request.target_language.strip()

    if not target_language or target_language == "English":
        return job["study_kit"]

    cached_translation = job_store.get_translation(
        request.job_id,
        target_language,
    )

    if cached_translation:
        return cached_translation

    try:
        translated_study_kit = translate_existing_study_kit(
            study_kit=job["study_kit"],
            target_language=target_language,
        )

        job_store.add_translation(
            request.job_id,
            target_language,
            translated_study_kit,
        )

        return translated_study_kit

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=build_translation_error_detail(
                raw_error=str(e),
                target_language=target_language,
                section="full study kit",
            ),
        )


@app.post("/translate-section")
def translate_section(request: TranslateSectionRequest):
    job = job_store.get_job(request.job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Study kit is not ready yet",
        )

    target_language = request.target_language.strip()
    section = request.section.strip()

    if not target_language or target_language == "English":
        return {
            "language": "English",
            "section": section,
            "data": get_original_section_data(
                study_kit=job["study_kit"],
                section=section,
                batch_start=request.batch_start or 0,
                batch_size=request.batch_size or 5,
            ),
            "cached": True,
            "is_complete": True,
        }

    section_key = build_translation_section_key(
        section=section,
        batch_start=request.batch_start or 0,
        batch_size=request.batch_size or 5,
    )

    cached_section = job_store.get_translation_section(
        job_id=request.job_id,
        language=target_language,
        section_key=section_key,
    )

    if cached_section is not None:
        return {
            "language": target_language,
            "section": section,
            "data": cached_section.get("data"),
            "cached": True,
            "is_complete": cached_section.get("is_complete", True),
            "batch_start": cached_section.get("batch_start"),
            "batch_size": cached_section.get("batch_size"),
        }

    try:
        translated_result = translate_study_kit_section(
            study_kit=job["study_kit"],
            target_language=target_language,
            section=section,
            batch_start=request.batch_start or 0,
            batch_size=request.batch_size or 5,
        )

        job_store.set_translation_section(
            job_id=request.job_id,
            language=target_language,
            section_key=section_key,
            translated_data=translated_result,
        )

        return {
            "language": target_language,
            "section": section,
            "data": translated_result.get("data"),
            "cached": False,
            "is_complete": translated_result.get("is_complete", True),
            "batch_start": translated_result.get("batch_start"),
            "batch_size": translated_result.get("batch_size"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=build_translation_error_detail(
                raw_error=str(e),
                target_language=target_language,
                section=section,
            ),
        )

@app.post("/search", response_model=SearchResponse)
def semantic_search(request: SearchRequest):
    job = job_store.get_job(request.job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] == "failed":
        raise HTTPException(
            status_code=500,
            detail={
                "message": job.get("error", "Processing failed"),
                "raw_error": job.get("raw_error"),
                "error_code": job.get("error_code"),
                "can_continue_with_transcript": job.get(
                    "can_continue_with_transcript",
                    False,
                ),
            },
        )

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Job is not completed yet",
        )

    embeddings = job.get("embeddings", [])

    if not embeddings:
        study_kit = job.get("study_kit")
        transcript_chunks = (
            get_study_kit_value(study_kit, "transcript_chunks")
            if study_kit
            else []
        )
        transcript_chunks = normalize_transcript_chunk_objects(transcript_chunks)

        if not transcript_chunks:
            raise HTTPException(
                status_code=400,
                detail="No transcript chunks found for search",
            )

        embeddings = agent3.create_search_embeddings(
            transcript_chunks,
        )
        job_store.update_job(
            request.job_id,
            embeddings=embeddings,
            search_index_status="ready",
            search_index_error="",
        )

    search_query = request.query

    if request.target_language and request.target_language != "English":
        search_query = translate_search_query_to_english(
            query=request.query,
            source_language=request.target_language,
        )

    query_embedding = create_embedding(search_query)

    scored_results = []

    for item in embeddings:
        chunk = item["chunk"]
        chunk_embedding = item["embedding"]

        score = cosine_similarity(query_embedding, chunk_embedding)

        result_text = chunk.text

        if request.target_language and request.target_language != "English":
            result_text = translate_short_text(
                text=chunk.text,
                target_language=request.target_language,
            )

        scored_results.append(
            SearchResult(
                text=result_text,
                start=chunk.start,
                end=chunk.end,
                start_time=format_timestamp(chunk.start),
                end_time=format_timestamp(chunk.end),
                score=score,
            )
        )

    scored_results.sort(key=lambda x: x.score, reverse=True)

    return SearchResponse(
        query=request.query,
        results=scored_results[: request.top_k],
    )


@app.post("/live-agent", response_model=LiveAgentResponse)
def live_agent(request: LiveAgentRequest):
    job = job_store.get_job(request.job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Study kit is not ready yet",
        )

    study_kit = get_study_kit_dict(job["study_kit"])
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        context_cards = build_live_agent_context_cards(study_kit, request)
        prompt_context = build_live_agent_context(study_kit, request)

        reply = generate_text(
            system_prompt=f"""
You are LectureForge Live Agent, a concise real-time learning coach.

Help the learner based on the lecture context, the active workspace tab, and
whether they are using voice or screen sharing. Give practical, immediate
feedback. If the student asks for something outside the lecture, answer briefly
and connect it back to the lecture when useful.

Respond in {request.target_language or "English"}.
""",
            user_prompt=f"""
Current app context:
{prompt_context}

Learner message:
{user_message}
""",
        )

        return LiveAgentResponse(
            reply=reply.strip(),
            context_cards=context_cards,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Live agent failed to respond",
                "raw_error": str(e),
            },
        )


def build_live_agent_context_cards(study_kit, request: LiveAgentRequest):
    cards = [
        f"Lecture: {study_kit.get('lecture_title', 'Untitled lecture')}",
        f"Active view: {request.active_tab or 'workspace'}",
    ]

    if request.voice_enabled:
        cards.append("Voice input active")

    if request.screen_shared:
        cards.append("Screen sharing active")

    outline = study_kit.get("outline", [])
    if outline:
        first_item = outline[0]
        cards.append(
            f"Current anchor: {first_item.get('title', 'Opening section')}"
        )

    return cards[:4]


def build_live_agent_context(study_kit, request: LiveAgentRequest):
    outline = study_kit.get("outline", [])[:6]
    key_concepts = study_kit.get("key_concepts", [])[:8]
    transcript_chunks = study_kit.get("transcript_chunks", [])[:4]

    outline_lines = [
        f"- {item.get('start_time', '')} {item.get('title', '')}: {item.get('summary', '')}"
        for item in outline
    ]

    concept_lines = [
        f"- {item.get('timestamp_time', '')} {item.get('concept', '')}: {item.get('explanation', '')}"
        for item in key_concepts
    ]

    transcript_lines = [
        f"- {item.get('start_time', '')}: {item.get('text', '')}"
        for item in transcript_chunks
    ]

    screen_context = (
        "The learner is sharing their screen, so reference the visible workspace "
        "and ask them to point out anything that is not captured in app context."
        if request.screen_shared
        else "The learner is not sharing their screen."
    )

    voice_context = (
        "The learner is using voice input; keep the response easy to follow aloud."
        if request.voice_enabled
        else "The learner is typing."
    )

    return "\n".join(
        [
            f"Lecture title: {study_kit.get('lecture_title', 'Untitled lecture')}",
            f"Active tab: {request.active_tab or 'workspace'}",
            f"Target language: {request.target_language or 'English'}",
            screen_context,
            voice_context,
            "Outline:",
            "\n".join(outline_lines) or "- No outline available",
            "Key concepts:",
            "\n".join(concept_lines) or "- No concepts available",
            "Opening transcript context:",
            "\n".join(transcript_lines) or "- No transcript available",
        ]
    )


def normalize_transcript_chunks_to_english(transcript_chunks):
    if not transcript_chunks:
        return transcript_chunks

    normalized_chunks = []
    batch_size = 20

    for batch_start in range(0, len(transcript_chunks), batch_size):
        batch = transcript_chunks[batch_start : batch_start + batch_size]
        payload = [
            {
                "index": batch_start + index,
                "start": chunk.start,
                "end": chunk.end,
                "text": chunk.text,
            }
            for index, chunk in enumerate(batch)
        ]

        system_prompt = """
You convert noisy lecture transcript chunks into clear English.

Return valid JSON only.

Schema:
{
  "chunks": [
    {
      "index": number,
      "text": "English translation"
    }
  ]
}

Rules:
- Translate all non-English text into natural English.
- Repair noisy ASR, romanized Telugu/Hindi/Indian-English code-mixed phrases, and literal word salad into coherent English.
- If a chunk mixes English words with non-English grammar, infer the intended lecture meaning and rewrite it in natural English.
- If a chunk is already clear English, keep it in English and lightly clean it.
- Preserve meaning and important details. Do not summarize.
- Preserve the index values exactly.
"""

        translated = generate_json(
            system_prompt=system_prompt,
            user_prompt=(
                "Convert these transcript chunks into clear English JSON.\n"
                f"{json.dumps(payload, ensure_ascii=False)}"
            ),
        )

        translated_by_index = {
            int(item.get("index")): item.get("text", "")
            for item in translated.get("chunks", [])
            if item.get("index") is not None
        }

        for index, chunk in enumerate(batch):
            original_index = batch_start + index
            translated_text = translated_by_index.get(original_index)

            if translated_text:
                chunk.text = translated_text

            normalized_chunks.append(chunk)

    return normalized_chunks


def transcript_looks_english(transcript_chunks):
    sample = " ".join(chunk.text for chunk in transcript_chunks[:6])

    if not sample.strip():
        return True

    ascii_letters = sum(1 for char in sample if char.isascii() and char.isalpha())
    non_ascii_letters = sum(1 for char in sample if not char.isascii() and char.isalpha())
    common_english_words = {
        "the",
        "and",
        "to",
        "of",
        "in",
        "that",
        "is",
        "for",
        "with",
        "this",
        "you",
        "we",
        "are",
    }
    words = [
        word.strip(".,!?;:()[]{}\"'").lower()
        for word in sample.split()
    ]
    english_hits = sum(1 for word in words if word in common_english_words)

    if non_ascii_letters > ascii_letters * 0.2:
        return False

    return english_hits >= 3 or non_ascii_letters == 0


def translate_existing_study_kit(study_kit, target_language: str):
    study_kit_dict = get_study_kit_dict(study_kit)

    translation_payload = {
        "lecture_title": study_kit_dict.get("lecture_title"),
        "transcript_chunks": study_kit_dict.get("transcript_chunks", []),
        "outline": study_kit_dict.get("outline", []),
        "key_concepts": study_kit_dict.get("key_concepts", []),
        "summaries": study_kit_dict.get("summaries", {}),
        "flashcards": study_kit_dict.get("flashcards", []),
        "concept_map": study_kit_dict.get("concept_map", {}),
    }

    system_prompt = f"""
You are a precise educational translation assistant.

Translate the provided study kit content into {target_language}.

Return valid JSON only.

You must return this exact JSON object shape:

{{
  "translated_study_kit": {{
    "lecture_title": "...",
    "transcript_chunks": [],
    "outline": [],
    "key_concepts": [],
    "summaries": {{}},
    "flashcards": [],
    "concept_map": {{}}
  }}
}}

Rules:
- Preserve the exact same top-level keys inside translated_study_kit.
- Preserve all timestamps exactly.
- Preserve all numeric fields exactly.
- Preserve all ids exactly.
- Preserve concept_map node ids exactly.
- Preserve concept_map edge source and target values exactly.
- Preserve start, end, start_time, end_time, timestamp, and timestamp_time exactly.
- Translate transcript_chunks.text.
- Translate outline.title and outline.summary.
- Translate key_concepts.concept and key_concepts.explanation.
- Translate summaries.short_summary, summaries.medium_summary, and summaries.full_summary.
- Translate flashcards.question and flashcards.answer.
- Translate concept_map.nodes.label.
- Translate concept_map.edges.label if present.
- Do not translate technical identifier fields such as id, source, target, or type.
- Keep programming words like Python, array, append, reverse, list, generator expression, and typecode understandable.
- If a programming term is commonly used in English, keep the English term and explain naturally in {target_language}.
"""

    user_prompt = f"""
Translate this complete study kit into {target_language}.

Return only the required JSON object.

Study kit:
{json.dumps(translation_payload, ensure_ascii=False)}
"""

    translated_payload = generate_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    translated_section = translated_payload.get("translated_study_kit")

    if not isinstance(translated_section, dict):
        raise ValueError(
            "Translation response did not contain translated_study_kit"
        )

    translated_study_kit = deepcopy(study_kit_dict)

    translated_study_kit["lecture_title"] = translated_section.get(
        "lecture_title",
        study_kit_dict.get("lecture_title"),
    )

    translated_study_kit["transcript_chunks"] = translated_section.get(
        "transcript_chunks",
        study_kit_dict.get("transcript_chunks", []),
    )

    translated_study_kit["outline"] = translated_section.get(
        "outline",
        study_kit_dict.get("outline", []),
    )

    translated_study_kit["key_concepts"] = translated_section.get(
        "key_concepts",
        study_kit_dict.get("key_concepts", []),
    )

    translated_study_kit["summaries"] = translated_section.get(
        "summaries",
        study_kit_dict.get("summaries", {}),
    )

    translated_study_kit["flashcards"] = translated_section.get(
        "flashcards",
        study_kit_dict.get("flashcards", []),
    )

    translated_study_kit["concept_map"] = translated_section.get(
        "concept_map",
        study_kit_dict.get("concept_map", {}),
    )

    translated_study_kit["bilingual_output"] = {
        "source_language": "English",
        "target_language": target_language,
    }

    return translated_study_kit


def translate_search_query_to_english(query: str, source_language: str):
    system_prompt = """
You translate search queries into English for semantic search.

Rules:
- Return only the translated query.
- Do not add explanations.
- Preserve technical terms where appropriate.
"""

    user_prompt = f"""
Translate this search query from {source_language} to English:

{query}
"""

    return generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    ).strip()


def translate_short_text(text: str, target_language: str):
    system_prompt = f"""
You translate short lecture transcript snippets into {target_language}.

Rules:
- Return only the translated text.
- Do not add explanations.
- Preserve technical programming terms when appropriate.
"""

    user_prompt = f"""
Translate this text into {target_language}:

{text}
"""

    return generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    ).strip()


def extract_json_from_text(text: str):
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("Translation response did not contain valid JSON")

        return json.loads(cleaned[start : end + 1])


def cosine_similarity(a, b) -> float:
    a = np.array(a)
    b = np.array(b)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


def build_translation_section_key(section: str, batch_start: int = 0, batch_size: int = 5):
    if section == "transcript_chunks":
        return f"{section}:{batch_start}:{batch_size}"

    return section


def get_study_kit_dict(study_kit):
    return (
        study_kit.model_dump()
        if hasattr(study_kit, "model_dump")
        else dict(study_kit)
    )


def extract_youtube_video_id_safe(youtube_url: str):
    try:
        return agent1._extract_video_id(youtube_url)
    except Exception:
        return None


def get_study_kit_value(study_kit, key: str):
    if isinstance(study_kit, dict):
        return study_kit.get(key)

    return getattr(study_kit, key, None)


def normalize_transcript_chunk_objects(chunks):
    normalized_chunks = []

    for chunk in chunks:
        if isinstance(chunk, TranscriptChunk):
            normalized_chunks.append(chunk)
            continue

        if isinstance(chunk, dict):
            normalized_chunks.append(
                TranscriptChunk(
                    start=float(chunk.get("start", 0)),
                    end=float(chunk.get("end", chunk.get("start", 0) + 2)),
                    text=chunk.get("text", ""),
                )
            )

    return normalized_chunks


def get_original_section_data(study_kit, section: str, batch_start: int = 0, batch_size: int = 5):
    study_kit_dict = get_study_kit_dict(study_kit)

    if section == "lecture_title":
        return study_kit_dict.get("lecture_title")

    if section == "transcript_chunks":
        chunks = study_kit_dict.get("transcript_chunks", [])
        return chunks[batch_start : batch_start + batch_size]

    if section in [
        "outline",
        "key_concepts",
        "summaries",
        "flashcards",
        "concept_map",
    ]:
        return study_kit_dict.get(section)

    raise ValueError(f"Unsupported translation section: {section}")


def translate_study_kit_section(
    study_kit,
    target_language: str,
    section: str,
    batch_start: int = 0,
    batch_size: int = 5,
):
    study_kit_dict = get_study_kit_dict(study_kit)

    supported_sections = {
        "lecture_title",
        "outline",
        "key_concepts",
        "summaries",
        "flashcards",
        "concept_map",
        "transcript_chunks",
    }

    if section not in supported_sections:
        raise ValueError(f"Unsupported translation section: {section}")

    if section == "transcript_chunks":
        all_chunks = study_kit_dict.get("transcript_chunks", [])
        batch = all_chunks[batch_start : batch_start + batch_size]

        translated_batch = translate_json_section(
            payload=batch,
            target_language=target_language,
            section=section,
        )

        is_complete = batch_start + batch_size >= len(all_chunks)

        return {
            "data": translated_batch,
            "batch_start": batch_start,
            "batch_size": batch_size,
            "is_complete": is_complete,
        }

    payload = study_kit_dict.get(section)

    translated_data = translate_json_section(
        payload=payload,
        target_language=target_language,
        section=section,
    )

    return {
        "data": translated_data,
        "batch_start": None,
        "batch_size": None,
        "is_complete": True,
    }


def translate_json_section(payload, target_language: str, section: str):
    system_prompt = f"""
You are a precise educational translation assistant.

Translate the provided JSON section into {target_language}.

Return valid JSON only.

You must return this exact JSON object shape:

{{
  "translated": null
}}

The value of "translated" must contain the translated version of the input payload.

Rules:
- Preserve the exact same JSON structure inside translated.
- Preserve all numeric values exactly.
- Preserve timestamps exactly.
- Preserve start, end, start_time, end_time, timestamp, and timestamp_time exactly.
- Preserve ids exactly.
- Preserve source and target exactly.
- Preserve type exactly.
- Translate only human-readable educational text fields.
- For transcript_chunks, translate only text.
- For outline, translate title and summary.
- For key_concepts, translate concept and explanation.
- For summaries, translate short_summary, medium_summary, and full_summary.
- For flashcards, translate question and answer.
- For concept_map, translate node labels and edge labels only.
- Keep programming terms like Python, array, append, reverse, list, generator expression, and typecode understandable.
- If a programming term is commonly used in English, you may keep the English term.
"""

    user_prompt = f"""
Section name: {section}

Translate this JSON section into {target_language}.

Return only the required JSON object.

Payload:
{json.dumps(payload, ensure_ascii=False)}
"""

    translated_payload = generate_json(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    if "translated" not in translated_payload:
        raise ValueError("Translation response did not contain translated field")

    return translated_payload["translated"]

def build_translation_error_detail(
    raw_error: str,
    target_language: str,
    section: str,
):
    lower_error = raw_error.lower()

    if "maximum context length" in lower_error or "context_length_exceeded" in lower_error:
        return {
            "message": (
                f"Translation failed because the {section} content is too long. "
                "Please retry section-by-section or use a shorter lecture."
            ),
            "raw_error": raw_error,
            "error_code": "TRANSLATION_CONTEXT_LENGTH_ERROR",
            "target_language": target_language,
            "section": section,
        }

    if "insufficient_quota" in lower_error or "exceeded your current quota" in lower_error:
        return {
            "message": (
                "Translation failed because OpenAI quota or billing is not available."
            ),
            "raw_error": raw_error,
            "error_code": "TRANSLATION_OPENAI_QUOTA_ERROR",
            "target_language": target_language,
            "section": section,
        }

    if "rate_limit" in lower_error or ("openai" in lower_error and "429" in lower_error):
        return {
            "message": (
                "Translation was rate-limited. Please retry after a short delay."
            ),
            "raw_error": raw_error,
            "error_code": "TRANSLATION_RATE_LIMIT",
            "target_language": target_language,
            "section": section,
        }

    if (
        "json" in lower_error
        or "validation error" in lower_error
        or "field required" in lower_error
        or "translated" in lower_error
    ):
        return {
            "message": (
                f"Translation failed because the model response for {section} did not match the expected structure. "
                "Please retry this section."
            ),
            "raw_error": raw_error,
            "error_code": "TRANSLATION_SCHEMA_ERROR",
            "target_language": target_language,
            "section": section,
        }

    return {
        "message": (
            f"Translation failed for {section}. Please retry or choose another language."
        ),
        "raw_error": raw_error,
        "error_code": "TRANSLATION_ERROR",
        "target_language": target_language,
        "section": section,
    }

def build_public_error_message(raw_error: str):
    lower_error = raw_error.lower()

    if "hosted audio transcription is disabled on serverless runtime" in lower_error:
        return {
            "error_code": "SERVERLESS_AUDIO_TRANSCRIPTION_UNAVAILABLE",
            "message": (
                "This video does not expose usable captions, and hosted audio "
                "transcription is disabled on the serverless backend to avoid long "
                "timeouts. Use a captioned lecture, paste a transcript, or run the "
                "backend on a worker service for no-caption videos."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if (
        "downloaded audio is too large" in lower_error
        or "maximum content length" in lower_error
        or "request entity too large" in lower_error
        or "413" in lower_error
    ):
        return {
            "error_code": "OPENAI_AUDIO_TOO_LARGE",
            "message": (
                "This video's audio is too large for the current OpenAI "
                "transcription request. Use a shorter video, a captioned video, "
                "or process the audio in chunks with a background worker."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if "openai whisper" in lower_error and (
        "insufficient_quota" in lower_error
        or "exceeded your current quota" in lower_error
    ):
        return {
            "error_code": "OPENAI_QUOTA_ERROR",
            "message": (
                "OpenAI rejected audio transcription because quota or billing is not available."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if "openai whisper" in lower_error and (
        "rate_limit" in lower_error
        or "429" in lower_error
        or "too many requests" in lower_error
    ):
        return {
            "error_code": "OPENAI_RATE_LIMIT",
            "message": (
                "OpenAI rate-limited audio transcription. Please retry after a short delay."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if "openai whisper" in lower_error and (
        "incorrect api key" in lower_error
        or "invalid api key" in lower_error
        or "401" in lower_error
    ):
        return {
            "error_code": "OPENAI_AUTH_ERROR",
            "message": (
                "OpenAI rejected the backend API key. Check the Render OPENAI_API_KEY value."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if "openai whisper" in lower_error and "transcription failed" in lower_error:
        return {
            "error_code": "OPENAI_TRANSCRIPTION_ERROR",
            "message": (
                "OpenAI could not transcribe this video from the hosted backend. "
                "Use a captioned lecture, paste a transcript, or run audio "
                "transcription from a longer-lived backend worker."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if "supadata request failed" in lower_error:
        return {
            "error_code": "SUPADATA_TRANSCRIPT_ERROR",
            "message": (
                "The hosted transcript service could not extract this video transcript. "
                "Try another public lecture URL."
            ),
            "can_continue_with_transcript": True,
            "raw_error": raw_error,
        }

    if "supadata_api_key is not configured" in lower_error:
        return {
            "error_code": "SUPADATA_CONFIG_ERROR",
            "message": (
                "SUPADATA_API_KEY is not configured in the backend environment variables."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if (
        "youtube is blocking requests from your ip" in lower_error
        or "sign in to confirm" in lower_error
        or "not a bot" in lower_error
        or "cloud provider" in lower_error
        or ("http error 429" in lower_error and "youtube" in lower_error)
        or ("too many requests" in lower_error and "youtube" in lower_error)
    ):
        return {
            "error_code": "YOUTUBE_CLOUD_IP_BLOCKED",
            "message": (
                "YouTube blocked transcript extraction from the deployed server. "
                "This often happens on cloud-hosted IPs."
            ),
            "can_continue_with_transcript": True,
            "raw_error": raw_error,
        }

    if "http error 403" in lower_error or "forbidden" in lower_error:
        return {
            "error_code": "YOUTUBE_ACCESS_BLOCKED",
            "message": (
                "YouTube blocked automated access to this video. Try a different public lecture URL."
            ),
            "can_continue_with_transcript": True,
            "raw_error": raw_error,
        }

    if "no captions" in lower_error or "no transcript" in lower_error:
        return {
            "error_code": "NO_TRANSCRIPT_AVAILABLE",
            "message": (
                "No accessible captions were found for this YouTube video. Try another video with captions."
            ),
            "can_continue_with_transcript": True,
            "raw_error": raw_error,
        }

    if "insufficient_quota" in lower_error or "exceeded your current quota" in lower_error:
        return {
            "error_code": "OPENAI_QUOTA_ERROR",
            "message": (
                "OpenAI rejected the request because the account has insufficient quota or billing is not active."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if "rate_limit" in lower_error or ("openai" in lower_error and "429" in lower_error):
        return {
            "error_code": "OPENAI_RATE_LIMIT",
            "message": (
                "OpenAI rate-limited the request. Please retry after a short delay."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if "incorrect api key" in lower_error or "invalid api key" in lower_error or "401" in lower_error:
        return {
            "error_code": "OPENAI_AUTH_ERROR",
            "message": (
                "OpenAI rejected the API key. Check that the Render OPENAI_API_KEY value is valid and not revoked."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if "model_not_found" in lower_error or "does not have access to model" in lower_error:
        return {
            "error_code": "OPENAI_MODEL_ERROR",
            "message": (
                "OpenAI rejected the model name. Check OPENAI_MODEL and OPENAI_EMBEDDING_MODEL in Render."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if "maximum context length" in lower_error or "context_length_exceeded" in lower_error:
        return {
            "error_code": "OPENAI_CONTEXT_LENGTH_ERROR",
            "message": (
                "The lecture transcript is too long for the current model call. "
                "Use a shorter video or chunk the analysis step."
            ),
            "can_continue_with_transcript": True,
            "raw_error": raw_error,
        }

    if "facultyauditreport" in lower_error:
        return {
        "error_code": "FACULTY_AUDIT_SCHEMA_ERROR",
        "message": (
            "The model returned a faculty audit response that did not match the required structure. "
            "Please retry, or use a shorter lecture."
        ),
        "can_continue_with_transcript": False,
        "raw_error": raw_error,
    }

    if (
    "json" in lower_error
    or "validation error" in lower_error
    or "field required" in lower_error
    or "pydantic" in lower_error
):
        return {
        "error_code": "MODEL_SCHEMA_ERROR",
        "message": (
            "The model returned a response that did not match the expected structure. "
            "Please retry the request."
        ),
        "can_continue_with_transcript": False,
        "raw_error": raw_error,
    }
    if "empty" in lower_error:
        return {
            "error_code": "EMPTY_INPUT",
            "message": "The provided transcript or extracted transcript was empty.",
            "can_continue_with_transcript": True,
            "raw_error": raw_error,
        }

    return {
        "error_code": "PROCESSING_ERROR",
        "message": (
            "Processing failed unexpectedly. Please retry with another YouTube URL."
        ),
        "can_continue_with_transcript": True,
        "raw_error": raw_error,
    }
