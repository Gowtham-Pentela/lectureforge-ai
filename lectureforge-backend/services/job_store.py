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
            "error": None,
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
        error: str = None,
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
        if error is not None:
            self.jobs[job_id]["error"] = error
        if error_code is not None:
            self.jobs[job_id]["error_code"] = error_code
        if can_continue_with_transcript is not None:
            self.jobs[job_id]["can_continue_with_transcript"] = can_continue_with_transcript
        if embeddings is not None:
            self.jobs[job_id]["embeddings"] = embeddings

    def get_job(self, job_id: str):
        return self.jobs.get(job_id)