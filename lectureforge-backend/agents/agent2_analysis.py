from typing import List
from models.schemas import TranscriptChunk, LectureAnalysis, OutlineItem, KeyConcept
from utils.transcript_utils import transcript_to_plain_text
from services.openai_service import generate_json


class Agent2Analysis:
    def analyze(self, transcript_chunks: List[TranscriptChunk]) -> LectureAnalysis:
        transcript_text = transcript_to_plain_text(transcript_chunks)

        system_prompt = """
You are an expert academic lecture analyst.

Your job:
1. Understand the structure of a lecture transcript.
2. Create a timestamped outline.
3. Extract the most important concepts.

Return valid JSON only.

Required JSON schema:
{
  "title": "string",
  "outline": [
    {
      "title": "string",
      "start": number,
      "end": number,
      "summary": "string"
    }
  ],
  "key_concepts": [
    {
      "concept": "string",
      "explanation": "string",
      "timestamp": number
    }
  ]
}
"""

        user_prompt = f"""
Analyze this lecture transcript.

Transcript:
{transcript_text}
"""

        data = generate_json(system_prompt, user_prompt)

        return LectureAnalysis(
            title=data.get("title", "Untitled Lecture"),
            outline=[
                OutlineItem(
                    title=item.get("title", ""),
                    start=float(item.get("start", 0)),
                    end=float(item.get("end", 0)),
                    summary=item.get("summary", ""),
                )
                for item in data.get("outline", [])
            ],
            key_concepts=[
                KeyConcept(
                    concept=item.get("concept", ""),
                    explanation=item.get("explanation", ""),
                    timestamp=float(item.get("timestamp", 0)),
                )
                for item in data.get("key_concepts", [])
            ],
        )