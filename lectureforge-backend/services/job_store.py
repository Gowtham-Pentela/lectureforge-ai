# lectureforge-backend/services/job_store.py

from typing import Any, Dict, Optional


class JobStore:
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self, job_id: str):
        self.jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "message": "Job queued",
            "error": None,
            "raw_error": None,
            "error_code": None,
            "can_continue_with_transcript": False,
            "study_kit": None,
            "faculty_audit": None,
            "embeddings": [],
            "translations": {},
            "translation_sections": {},
        }

    def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        raw_error: Optional[str] = None,
        error_code: Optional[str] = None,
        can_continue_with_transcript: Optional[bool] = None,
        study_kit: Any = None,
        faculty_audit: Any = None,
        embeddings: Any = None,
    ):
        if job_id not in self.jobs:
            return

        job = self.jobs[job_id]

        if status is not None:
            job["status"] = status

        if progress is not None:
            job["progress"] = progress

        if message is not None:
            job["message"] = message

        if error is not None:
            job["error"] = error

        if raw_error is not None:
            job["raw_error"] = raw_error

        if error_code is not None:
            job["error_code"] = error_code

        if can_continue_with_transcript is not None:
            job["can_continue_with_transcript"] = can_continue_with_transcript

        if study_kit is not None:
            job["study_kit"] = study_kit

        if faculty_audit is not None:
            job["faculty_audit"] = faculty_audit

        if embeddings is not None:
            job["embeddings"] = embeddings

    def get_job(self, job_id: str):
        return self.jobs.get(job_id)

    def add_translation(
        self,
        job_id: str,
        target_language: str,
        translated_study_kit: Any,
    ):
        if job_id not in self.jobs:
            return

        self.jobs[job_id].setdefault("translations", {})
        self.jobs[job_id]["translations"][target_language] = translated_study_kit

    def get_translation(
        self,
        job_id: str,
        target_language: str,
    ):
        if job_id not in self.jobs:
            return None

        translations = self.jobs[job_id].get("translations", {})
        return translations.get(target_language)

    def set_translation_section(
        self,
        job_id: str,
        language: str,
        section_key: str,
        translated_data: Any,
    ):
        if job_id not in self.jobs:
            return

        self.jobs[job_id].setdefault("translation_sections", {})
        self.jobs[job_id]["translation_sections"].setdefault(language, {})
        self.jobs[job_id]["translation_sections"][language][section_key] = translated_data

    def get_translation_section(
        self,
        job_id: str,
        language: str,
        section_key: str,
    ):
        if job_id not in self.jobs:
            return None

        return (
            self.jobs[job_id]
            .get("translation_sections", {})
            .get(language, {})
            .get(section_key)
        )