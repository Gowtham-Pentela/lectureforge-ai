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
    LectureAnalysis,
    TranslateStudyKitRequest,
    TranslateSectionRequest,
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

    asyncio.create_task(
        run_video_processing_pipeline(
            job_id=job_id,
            youtube_url=request.youtube_url,
            target_language="English",
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
        message="Agent 3 is generating English study kit",
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
                "can_continue_with_transcript": job.get(
                    "can_continue_with_transcript",
                    False,
                ),
            },
        )

    if job["status"] != "completed":
        raise HTTPException(
            status_code=202,
            detail="Study kit is not ready yet",
        )

    return job["study_kit"]


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
        public_error = build_public_error_message(str(e))

        raise HTTPException(
            status_code=500,
            detail={
                "message": public_error["message"],
                "raw_error": public_error.get("raw_error"),
                "error_code": public_error["error_code"],
            },
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
        public_error = build_public_error_message(str(e))

        raise HTTPException(
            status_code=500,
            detail={
                "message": public_error["message"],
                "raw_error": public_error.get("raw_error"),
                "error_code": public_error["error_code"],
            },
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
        raise HTTPException(
            status_code=400,
            detail="No search index found",
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


def translate_existing_study_kit(study_kit, target_language: str):
    study_kit_dict = (
        study_kit.model_dump()
        if hasattr(study_kit, "model_dump")
        else dict(study_kit)
    )

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

Very important rules:
- Preserve the exact same top-level JSON keys.
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
Translate this complete study kit into {target_language}:

{json.dumps(translation_payload, ensure_ascii=False)}
"""

    translated_text = generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    translated_payload = extract_json_from_text(translated_text)

    translated_study_kit = deepcopy(study_kit_dict)

    translated_study_kit["lecture_title"] = translated_payload.get(
        "lecture_title",
        study_kit_dict.get("lecture_title"),
    )

    translated_study_kit["transcript_chunks"] = translated_payload.get(
        "transcript_chunks",
        study_kit_dict.get("transcript_chunks", []),
    )

    translated_study_kit["outline"] = translated_payload.get(
        "outline",
        study_kit_dict.get("outline", []),
    )

    translated_study_kit["key_concepts"] = translated_payload.get(
        "key_concepts",
        study_kit_dict.get("key_concepts", []),
    )

    translated_study_kit["summaries"] = translated_payload.get(
        "summaries",
        study_kit_dict.get("summaries", {}),
    )

    translated_study_kit["flashcards"] = translated_payload.get(
        "flashcards",
        study_kit_dict.get("flashcards", []),
    )

    translated_study_kit["concept_map"] = translated_payload.get(
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

Rules:
- Preserve the exact same JSON structure.
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

Translate this JSON section into {target_language}:

{json.dumps(payload, ensure_ascii=False)}
"""

    translated_text = generate_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    return extract_json_from_text(translated_text)

def build_public_error_message(raw_error: str):
    lower_error = raw_error.lower()

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

    if "json" in lower_error:
        return {
            "error_code": "MODEL_JSON_ERROR",
            "message": (
                "The model returned an invalid structured response. Please retry the request."
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