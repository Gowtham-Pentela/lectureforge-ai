import os
import uuid
import asyncio
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    ProcessVideoRequest,
    ProcessTranscriptRequest,
    ProcessVideoResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
    LectureAnalysis,
)

from services.job_store import JobStore
from services.openai_service import create_embedding, generate_text
from agents.agent1_ingestion import Agent1Ingestion
from agents.agent2_analysis import Agent2Analysis
from agents.agent3_study import Agent3Study
from utils.transcript_utils import plain_text_to_chunks, format_timestamp
from utils.study_kit_validator import validate_study_kit


app = FastAPI(
    title="LectureForge AI Backend",
    description="AI backend for turning YouTube lectures into student study kits",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


job_store = JobStore()

agent1 = Agent1Ingestion()
agent2 = Agent2Analysis()
agent3 = Agent3Study()


@app.get("/")
def root():
    return {
        "app": "LectureForge AI Backend",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/debug-env")
def debug_env():
    key = os.getenv("OPENAI_API_KEY")

    return {
        "openai_key_present": bool(key),
        "openai_key_prefix": key[:7] if key else None,
        "openai_key_length": len(key) if key else 0,
        "openai_model": os.getenv("OPENAI_MODEL"),
        "embedding_model": os.getenv("OPENAI_EMBEDDING_MODEL"),
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

    asyncio.create_task(
        run_video_processing_pipeline(
            job_id=job_id,
            youtube_url=request.youtube_url,
            target_language=request.target_language,
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
            target_language=request.target_language,
        )
    )

    return ProcessVideoResponse(
        job_id=job_id,
        status="queued",
        message="Transcript processing started",
    )


async def run_video_processing_pipeline(
    job_id: str,
    youtube_url: str,
    target_language: str,
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

        await run_common_study_pipeline(
            job_id=job_id,
            transcript_chunks=transcript_chunks,
            target_language=target_language,
            lecture_title_override=None,
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

    job_store.update_job(
        job_id,
        status="processing",
        progress=60,
        message="Agent 3 is generating study kit",
    )

    study_kit = await asyncio.to_thread(
        agent3.generate_study_kit,
        transcript_chunks,
        analysis,
        target_language,
    )

    study_kit = validate_study_kit(study_kit)

    job_store.update_job(
        job_id,
        status="processing",
        progress=85,
        message="Creating semantic search index",
    )

    embeddings = await asyncio.to_thread(
        agent3.create_search_embeddings,
        study_kit.transcript_chunks,
    )

    job_store.update_job(
        job_id,
        status="completed",
        progress=100,
        message="Study kit ready",
        study_kit=study_kit,
        embeddings=embeddings,
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
                "can_continue_with_transcript": job.get("can_continue_with_transcript", False),
            },
        )

    if job["status"] != "completed":
        raise HTTPException(
            status_code=202,
            detail="Study kit is not ready yet",
        )

    return job["study_kit"]


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
                "can_continue_with_transcript": job.get("can_continue_with_transcript", False),
            },
        )

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Job is not completed yet",
        )

    embeddings = job.get("embeddings", [])

    if not embeddings:
        raise HTTPException(
            status_code=400,
            detail="No search index found",
        )

    query_embedding = create_embedding(request.query)

    scored_results = []

    for item in embeddings:
        chunk = item["chunk"]
        chunk_embedding = item["embedding"]

        score = cosine_similarity(query_embedding, chunk_embedding)

        scored_results.append(
            SearchResult(
                text=chunk.text,
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


def cosine_similarity(a, b) -> float:
    a = np.array(a)
    b = np.array(b)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


def build_public_error_message(raw_error: str):
    lower_error = raw_error.lower()

    if "insufficient_quota" in lower_error or "exceeded your current quota" in lower_error:
        return {
            "error_code": "OPENAI_QUOTA_ERROR",
            "message": (
                "OpenAI rejected the request because the account has insufficient quota or billing is not active."
            ),
            "can_continue_with_transcript": False,
            "raw_error": raw_error,
        }

    if "rate_limit" in lower_error or "429" in lower_error:
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
                "The lecture transcript is too long for the current model call. Use a shorter video or chunk the analysis step."
            ),
            "can_continue_with_transcript": True,
            "raw_error": raw_error,
        }

    if "json" in lower_error:
        return {
            "error_code": "MODEL_JSON_ERROR",
            "message": (
                "The model returned an invalid structured response. Please retry the request."
            ),
            "can_continue_with_transcript": False,
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