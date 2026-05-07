from typing import Dict, Any


class JobStore:
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self, job_id: str):
        self.jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "message": "Job queued",
            "study_kit": None,
            "translations": {},
            "error": None,
            "raw_error": None,
            "error_code": None,
            "can_continue_with_transcript": False,
            "embeddings": [],
        }

    def update_job(
        self,
        job_id: str,
        status: str = None,
        progress: int = None,
        message: str = None,
        study_kit: Any = None,
        translations: Dict[str, Any] = None,
        error: str = None,
        raw_error: str = None,
        error_code: str = None,
        can_continue_with_transcript: bool = None,
        embeddings: Any = None,
    ):
        if job_id not in self.jobs:
            return

        if status is not None:
            self.jobs[job_id]["status"] = status

        if progress is not None:
            self.jobs[job_id]["progress"] = progress

        if message is not None:
            self.jobs[job_id]["message"] = message

        if study_kit is not None:
            self.jobs[job_id]["study_kit"] = study_kit

        if translations is not None:
            self.jobs[job_id]["translations"] = translations

        if error is not None:
            self.jobs[job_id]["error"] = error

        if raw_error is not None:
            self.jobs[job_id]["raw_error"] = raw_error

        if error_code is not None:
            self.jobs[job_id]["error_code"] = error_code

        if can_continue_with_transcript is not None:
            self.jobs[job_id]["can_continue_with_transcript"] = can_continue_with_transcript

        if embeddings is not None:
            self.jobs[job_id]["embeddings"] = embeddings

    def add_translation(self, job_id: str, language: str, translated_study_kit: Any):
        if job_id not in self.jobs:
            return

        if "translations" not in self.jobs[job_id]:
            self.jobs[job_id]["translations"] = {}

        self.jobs[job_id]["translations"][language] = translated_study_kit

    def get_translation(self, job_id: str, language: str):
        if job_id not in self.jobs:
            return None

        return self.jobs[job_id].get("translations", {}).get(language)

    def get_job(self, job_id: str):
        return self.jobs.get(job_id)