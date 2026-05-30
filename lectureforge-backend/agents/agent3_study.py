import re
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

        generated_assets = self._generate_study_assets(
            transcript_text=transcript_text,
            analysis=analysis,
        )

        summaries = generated_assets["summaries"]
        flashcards = generated_assets["flashcards"]
        concept_map = generated_assets["concept_map"]

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

    def _generate_study_assets(
        self,
        transcript_text: str,
        analysis: LectureAnalysis,
    ) -> Dict[str, Any]:
        outline_payload = [
            {
                "title": item.title,
                "start": item.start,
                "end": item.end,
                "summary": item.summary,
            }
            for item in analysis.outline
        ]
        concepts_payload = [
            {
                "concept": item.concept,
                "explanation": item.explanation,
                "timestamp": item.timestamp,
            }
            for item in analysis.key_concepts
        ]

        system_prompt = """
You are an expert study assistant and concept-map designer.

Create all student study assets in one pass.

Return valid JSON only.

Schema:
{
  "summaries": {
    "short_summary": "string",
    "medium_summary": "string",
    "full_summary": "string"
  },
  "flashcards": [
    {
      "question": "string",
      "answer": "string",
      "timestamp": number
    }
  ],
  "concept_map": {
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
}

Rules:
- Create 10 to 15 flashcards.
- Flashcard questions should test understanding, not memorization.
- Every flashcard must include a timestamp in seconds from the source moment.
- Concept map nodes should represent the lecture's idea hierarchy, not a flat list.
- Concept map edges must explain how ideas depend on, contrast with, enable, or lead to each other.
- Every concept map edge must refer to an existing node id.
- Prefer 8 to 15 concept map nodes.
- Use stable lowercase ids with underscores.
"""

        user_prompt = f"""
Lecture outline:
{outline_payload}

Key concepts:
{concepts_payload}

Transcript:
{transcript_text}
"""

        try:
            data = generate_json(system_prompt, user_prompt)
        except Exception as e:
            print(f"Combined study asset generation failed; using fallback: {str(e)}")
            return {
                "summaries": self._fallback_summaries(transcript_text),
                "flashcards": self._fallback_flashcards(transcript_text),
                "concept_map": self._fallback_concept_map(transcript_text),
            }

        if not isinstance(data, dict):
            data = {}

        summaries_data = data.get("summaries", {})
        flashcards_data = data.get("flashcards", [])
        concept_map_data = data.get("concept_map", {})

        if not isinstance(summaries_data, dict):
            summaries_data = {}

        if not isinstance(flashcards_data, list):
            flashcards_data = []

        if not isinstance(concept_map_data, dict):
            concept_map_data = {}

        nodes_data = concept_map_data.get("nodes", [])
        edges_data = concept_map_data.get("edges", [])

        if not isinstance(nodes_data, list):
            nodes_data = []

        if not isinstance(edges_data, list):
            edges_data = []

        return {
            "summaries": SummarySet(
                short_summary=self._as_text(summaries_data.get("short_summary")),
                medium_summary=self._as_text(summaries_data.get("medium_summary")),
                full_summary=self._as_text(summaries_data.get("full_summary")),
            ),
            "flashcards": [
                Flashcard(
                    question=self._as_text(item.get("question")),
                    answer=self._as_text(item.get("answer")),
                    timestamp=self._safe_float(item.get("timestamp"), 0),
                )
                for item in flashcards_data
                if isinstance(item, dict)
            ],
            "concept_map": ConceptMap(
                nodes=[
                    ConceptMapNode(
                        id=self._as_node_id(item.get("id"), f"concept_{index + 1}"),
                        label=self._as_text(item.get("label"), f"Concept {index + 1}"),
                        type=self._as_text(item.get("type"), "concept"),
                        timestamp=self._safe_float(item.get("timestamp"), 0)
                        if item.get("timestamp") is not None
                        else None,
                    )
                    for index, item in enumerate(nodes_data)
                    if isinstance(item, dict)
                ],
                edges=[
                    ConceptMapEdge(
                        source=self._as_text(item.get("source")),
                        target=self._as_text(item.get("target")),
                        label=self._as_text(item.get("label")),
                    )
                    for item in edges_data
                    if isinstance(item, dict)
                ],
            ),
        }

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

        try:
            data = generate_json(system_prompt, user_prompt)

            if not isinstance(data, dict):
                raise ValueError("Summary payload was not a JSON object")

            summaries = SummarySet(
                short_summary=str(data.get("short_summary") or ""),
                medium_summary=str(data.get("medium_summary") or ""),
                full_summary=str(data.get("full_summary") or ""),
            )

            if summaries.short_summary or summaries.medium_summary or summaries.full_summary:
                return summaries
        except Exception as e:
            print(f"Summary generation failed; using fallback: {str(e)}")

        return self._fallback_summaries(transcript_text)

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

        try:
            data = generate_json(system_prompt, user_prompt)

            if not isinstance(data, dict):
                raise ValueError("Flashcard payload was not a JSON object")

            flashcards_data = data.get("flashcards", [])

            if not isinstance(flashcards_data, list):
                raise ValueError("Flashcards payload was not a list")

            flashcards = [
                Flashcard(
                    question=str(item.get("question") or ""),
                    answer=str(item.get("answer") or ""),
                    timestamp=self._safe_float(item.get("timestamp"), 0),
                )
                for item in flashcards_data
                if isinstance(item, dict)
            ]

            if flashcards:
                return flashcards
        except Exception as e:
            print(f"Flashcard generation failed; using fallback: {str(e)}")

        return self._fallback_flashcards(transcript_text)

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

        try:
            data = generate_json(system_prompt, user_prompt)

            if not isinstance(data, dict):
                raise ValueError("Concept map payload was not a JSON object")

            nodes_data = data.get("nodes", [])
            edges_data = data.get("edges", [])

            if not isinstance(nodes_data, list):
                nodes_data = []

            if not isinstance(edges_data, list):
                edges_data = []

            concept_map = ConceptMap(
                nodes=[
                    ConceptMapNode(
                        id=str(item.get("id") or f"concept_{index + 1}"),
                        label=str(item.get("label") or f"Concept {index + 1}"),
                        type=str(item.get("type") or "concept"),
                        timestamp=self._safe_float(item.get("timestamp"), 0)
                        if item.get("timestamp") is not None
                        else None,
                    )
                    for index, item in enumerate(nodes_data)
                    if isinstance(item, dict)
                ],
                edges=[
                    ConceptMapEdge(
                        source=str(item.get("source") or ""),
                        target=str(item.get("target") or ""),
                        label=str(item.get("label") or ""),
                    )
                    for item in edges_data
                    if isinstance(item, dict)
                ],
            )

            if concept_map.nodes:
                return concept_map
        except Exception as e:
            print(f"Concept map generation failed; using fallback: {str(e)}")

        return self._fallback_concept_map(transcript_text)

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

    def _fallback_summaries(self, transcript_text: str) -> SummarySet:
        sentences = self._extract_sentences(transcript_text)
        short = " ".join(sentences[:3]) or "This lecture introduces and develops several connected ideas."
        medium = " ".join(sentences[:8]) or short
        full = " ".join(sentences[:16]) or medium

        return SummarySet(
            short_summary=short[:900],
            medium_summary=medium[:2200],
            full_summary=full[:5000],
        )

    def _fallback_flashcards(self, transcript_text: str) -> List[Flashcard]:
        chunks = self._extract_timestamped_chunks(transcript_text)
        flashcards = []

        for index, chunk in enumerate(chunks[:12]):
            answer = self._trim_text(chunk["text"], 260)

            if not answer:
                continue

            flashcards.append(
                Flashcard(
                    question=f"What is discussed around {chunk['time_label']}?",
                    answer=answer,
                    timestamp=chunk["start"],
                )
            )

        if flashcards:
            return flashcards

        return [
            Flashcard(
                question="What is the main takeaway from this lecture?",
                answer=self._trim_text(transcript_text, 260)
                or "Review the transcript to identify the central takeaway.",
                timestamp=0,
            )
        ]

    def _fallback_concept_map(self, transcript_text: str) -> ConceptMap:
        chunks = self._extract_timestamped_chunks(transcript_text)
        source_chunks = chunks[:8]

        if not source_chunks:
            source_chunks = [
                {
                    "start": 0,
                    "time_label": "00:00:00",
                    "text": sentence,
                }
                for sentence in self._extract_sentences(transcript_text)[:6]
            ]

        nodes = []

        for index, chunk in enumerate(source_chunks):
            nodes.append(
                ConceptMapNode(
                    id=f"concept_{index + 1}",
                    label=self._concept_label(chunk["text"], fallback=f"Concept {index + 1}"),
                    type="main_topic" if index == 0 else "subtopic",
                    timestamp=chunk["start"],
                )
            )

        edges = [
            ConceptMapEdge(
                source=nodes[index].id,
                target=nodes[index + 1].id,
                label="leads to",
            )
            for index in range(len(nodes) - 1)
        ]

        return ConceptMap(nodes=nodes, edges=edges)

    def _extract_timestamped_chunks(self, transcript_text: str) -> List[Dict[str, Any]]:
        pattern = re.compile(
            r"\[(?P<start>\d{2}:\d{2}:\d{2})\s*-\s*(?P<end>\d{2}:\d{2}:\d{2})\]\s*(?P<text>.*?)(?=\n\[|\Z)",
            re.DOTALL,
        )
        chunks = []

        for match in pattern.finditer(transcript_text or ""):
            text = re.sub(r"\s+", " ", match.group("text")).strip()

            if not text:
                continue

            chunks.append(
                {
                    "start": self._timestamp_to_seconds(match.group("start")),
                    "time_label": match.group("start"),
                    "text": text,
                }
            )

        return chunks

    def _extract_sentences(self, text: str) -> List[str]:
        cleaned = re.sub(r"\[[^\]]+\]", " ", text or "")
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        sentences = re.findall(r"[^.!?]+[.!?]", cleaned)

        if sentences:
            return [sentence.strip() for sentence in sentences if sentence.strip()]

        return [cleaned] if cleaned else []

    def _concept_label(self, text: str, fallback: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9\s-]", "", text or "")
        words = [
            word
            for word in cleaned.split()
            if len(word) > 2 and word.lower() not in {"the", "and", "for", "that", "this", "you"}
        ]

        if not words:
            return fallback

        return " ".join(words[:6]).capitalize()

    def _trim_text(self, text: str, max_chars: int) -> str:
        cleaned = re.sub(r"\s+", " ", text or "").strip()

        if len(cleaned) <= max_chars:
            return cleaned

        return cleaned[: max_chars - 1].rstrip() + "..."

    def _timestamp_to_seconds(self, timestamp: str) -> float:
        try:
            hours, minutes, seconds = timestamp.split(":")
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        except Exception:
            return 0

    def _safe_float(self, value, fallback: float) -> float:
        try:
            return float(value)
        except Exception:
            return fallback

    def _as_text(self, value, fallback: str = "") -> str:
        if value is None:
            return fallback

        if isinstance(value, (dict, list)):
            return fallback

        text = str(value).strip()
        return text if text else fallback

    def _as_node_id(self, value, fallback: str) -> str:
        text = self._as_text(value, fallback)
        text = re.sub(r"[^A-Za-z0-9_-]+", "_", text).strip("_").lower()
        return text or fallback
