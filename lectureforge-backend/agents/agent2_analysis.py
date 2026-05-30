import re
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

        try:
            data = generate_json(system_prompt, user_prompt)
            analysis = self._analysis_from_payload(data)

            if analysis.outline and analysis.key_concepts:
                return analysis
        except Exception as e:
            print(f"Agent 2 model analysis failed; using fallback: {str(e)}")

        return self._fallback_analysis(transcript_chunks)

    def _analysis_from_payload(self, data) -> LectureAnalysis:
        if not isinstance(data, dict):
            raise ValueError("Lecture analysis payload was not a JSON object")

        outline_data = data.get("outline", [])
        concepts_data = data.get("key_concepts", [])

        if not isinstance(outline_data, list):
            outline_data = []

        if not isinstance(concepts_data, list):
            concepts_data = []

        return LectureAnalysis(
            title=str(data.get("title") or "Untitled Lecture"),
            outline=[
                OutlineItem(
                    title=str(item.get("title") or "Lecture section"),
                    start=self._safe_float(item.get("start"), 0),
                    end=self._safe_float(item.get("end"), 0),
                    summary=str(item.get("summary") or ""),
                )
                for item in outline_data
                if isinstance(item, dict)
            ],
            key_concepts=[
                KeyConcept(
                    concept=str(item.get("concept") or "Key concept"),
                    explanation=str(item.get("explanation") or ""),
                    timestamp=self._safe_float(item.get("timestamp"), 0),
                )
                for item in concepts_data
                if isinstance(item, dict)
            ],
        )

    def _fallback_analysis(
        self,
        transcript_chunks: List[TranscriptChunk],
    ) -> LectureAnalysis:
        if not transcript_chunks:
            return LectureAnalysis(title="Lecture transcript", outline=[], key_concepts=[])

        outline = []
        chunk_count = len(transcript_chunks)
        section_count = min(max(chunk_count, 1), 6)
        section_size = max(1, round(chunk_count / section_count))

        for index in range(0, chunk_count, section_size):
            section = transcript_chunks[index : index + section_size]

            if not section:
                continue

            title = self._short_title(section[0].text, fallback=f"Section {len(outline) + 1}")
            summary = self._short_summary(" ".join(chunk.text for chunk in section))

            outline.append(
                OutlineItem(
                    title=title,
                    start=section[0].start,
                    end=section[-1].end,
                    summary=summary,
                )
            )

            if len(outline) >= 6:
                break

        concepts = [
            KeyConcept(
                concept=item.title,
                explanation=item.summary or "Important idea discussed in this lecture section.",
                timestamp=item.start,
            )
            for item in outline[:8]
        ]

        return LectureAnalysis(
            title=self._short_title(transcript_chunks[0].text, fallback="Lecture Study Kit"),
            outline=outline,
            key_concepts=concepts,
        )

    def _short_title(self, text: str, fallback: str) -> str:
        sentence = self._first_sentence(text)
        words = [
            word.strip(".,!?;:()[]{}\"'")
            for word in sentence.split()
            if word.strip(".,!?;:()[]{}\"'")
        ]

        if not words:
            return fallback

        return " ".join(words[:9]).capitalize()

    def _short_summary(self, text: str) -> str:
        sentence = self._first_sentence(text)

        if sentence:
            return sentence[:280]

        return "Important ideas from this part of the lecture."

    def _first_sentence(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text or "").strip()
        match = re.search(r"(.+?[.!?])(?:\s|$)", cleaned)

        if match:
            return match.group(1).strip()

        return cleaned[:180]

    def _safe_float(self, value, fallback: float) -> float:
        try:
            return float(value)
        except Exception:
            return fallback
