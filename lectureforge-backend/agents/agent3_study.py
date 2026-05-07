from typing import List, Dict, Any
from models.schemas import (
    TranscriptChunk,
    LectureAnalysis,
    SummarySet,
    Flashcard,
    ConceptMap,
    ConceptMapNode,
    ConceptMapEdge,
    StudyKit,
)
from utils.transcript_utils import transcript_to_plain_text
from services.openai_service import generate_json, create_embeddings


class Agent3Study:
    def generate_study_kit(
        self,
        transcript_chunks: List[TranscriptChunk],
        analysis: LectureAnalysis,
        target_language: str = "English",
    ) -> StudyKit:
        transcript_text = transcript_to_plain_text(transcript_chunks)

        summaries = self._generate_summaries(transcript_text)
        flashcards = self._generate_flashcards(transcript_text)
        concept_map = self._generate_concept_map(transcript_text)

        bilingual_output = None
        if target_language and target_language.lower() != "english":
            bilingual_output = self._generate_bilingual_output(
                transcript_text=transcript_text,
                target_language=target_language,
            )

        return StudyKit(
            lecture_title=analysis.title,
            transcript_chunks=transcript_chunks,
            outline=analysis.outline,
            key_concepts=analysis.key_concepts,
            summaries=summaries,
            flashcards=flashcards,
            concept_map=concept_map,
            bilingual_output=bilingual_output,
        )

    def _generate_summaries(self, transcript_text: str) -> SummarySet:
        system_prompt = """
You are an expert study assistant.

Create three summaries:
1. short_summary: readable in about 90 seconds
2. medium_summary: readable in about 5 minutes
3. full_summary: detailed but still student-friendly

Return valid JSON only.

Schema:
{
  "short_summary": "string",
  "medium_summary": "string",
  "full_summary": "string"
}
"""

        user_prompt = f"""
Create summaries for this lecture:

{transcript_text}
"""

        data = generate_json(system_prompt, user_prompt)

        return SummarySet(
            short_summary=data.get("short_summary", ""),
            medium_summary=data.get("medium_summary", ""),
            full_summary=data.get("full_summary", ""),
        )

    def _generate_flashcards(self, transcript_text: str) -> List[Flashcard]:
        system_prompt = """
You are an expert flashcard creator.

Create 10 to 15 high-quality flashcards from the lecture.

Rules:
- Questions should test understanding, not just memorization.
- Answers should be concise.
- Every flashcard must include the source timestamp in seconds.

Return valid JSON only.

Schema:
{
  "flashcards": [
    {
      "question": "string",
      "answer": "string",
      "timestamp": number
    }
  ]
}
"""

        user_prompt = f"""
Create flashcards from this lecture:

{transcript_text}
"""

        data = generate_json(system_prompt, user_prompt)

        return [
            Flashcard(
                question=item.get("question", ""),
                answer=item.get("answer", ""),
                timestamp=float(item.get("timestamp", 0)),
            )
            for item in data.get("flashcards", [])
        ]

    def _generate_concept_map(self, transcript_text: str) -> ConceptMap:
        system_prompt = """
You are an expert at creating concept maps for students.

Extract the main topics and show how they connect.

Return valid JSON only.

Schema:
{
  "nodes": [
    {
      "id": "short_unique_id",
      "label": "Human readable concept name",
      "type": "main_topic | subtopic | detail",
      "timestamp": number
    }
  ],
  "edges": [
    {
      "source": "node_id",
      "target": "node_id",
      "label": "relationship"
    }
  ]
}

Rules:
- Use stable lowercase ids with underscores.
- Do not create duplicate nodes.
- Every edge must refer to an existing node id.
- Prefer 8 to 15 nodes.
"""

        user_prompt = f"""
Create a concept map from this lecture:

{transcript_text}
"""

        data = generate_json(system_prompt, user_prompt)

        return ConceptMap(
            nodes=[
                ConceptMapNode(
                    id=item.get("id", ""),
                    label=item.get("label", ""),
                    type=item.get("type", "concept"),
                    timestamp=float(item.get("timestamp", 0))
                    if item.get("timestamp") is not None
                    else None,
                )
                for item in data.get("nodes", [])
            ],
            edges=[
                ConceptMapEdge(
                    source=item.get("source", ""),
                    target=item.get("target", ""),
                    label=item.get("label", ""),
                )
                for item in data.get("edges", [])
            ],
        )

    def _generate_bilingual_output(
        self,
        transcript_text: str,
        target_language: str,
    ) -> Dict[str, Any]:
        system_prompt = f"""
You are a bilingual academic study assistant.

Translate and simplify the lecture into {target_language}.

Return valid JSON only.

Schema:
{{
  "language": "{target_language}",
  "translated_summary": "string",
  "key_terms": [
    {{
      "english": "string",
      "translation": "string",
      "explanation": "string"
    }}
  ]
}}
"""

        user_prompt = f"""
Create bilingual study support for this lecture:

{transcript_text}
"""

        return generate_json(system_prompt, user_prompt)

    def create_search_embeddings(self, transcript_chunks: List[TranscriptChunk]):
        texts = [chunk.text for chunk in transcript_chunks]
        embeddings = create_embeddings(texts)

        return [
            {
                "chunk": transcript_chunks[i],
                "embedding": embeddings[i],
            }
            for i in range(len(transcript_chunks))
        ]