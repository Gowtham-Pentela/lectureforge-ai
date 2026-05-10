import json
from typing import Any, Dict

from models.schemas import (
    AuditDimension,
    FacultyAuditReport,
    HighestImpactFix,
    PriorityFix,
    TimestampedRewrite,
)
from services.openai_service import generate_json


FACULTY_AUDIT_SYSTEM_PROMPT = """
You are an expert instructional design reviewer helping a faculty member privately improve a lecture before publishing it.

This report is voluntary, private, and instructor-facing.
It is not surveillance.
It is not a faculty performance evaluation.
Do not assign grades, scores, rankings, or labels to the instructor.
Do not use punitive, judgmental, or accusatory language.

Your role is to produce practical, evidence-based feedback that helps the instructor improve student understanding.

Audit the lecture across:
1. Pedagogical clarity
2. Accessibility
3. Equity and inclusion
4. Structure and pacing
5. Cognitive load
6. Student engagement

Core principles:
- Use only evidence from the transcript.
- Do not invent lecture content.
- Do not invent timestamps.
- If evidence is insufficient, say so.
- Be specific, respectful, and actionable.
- Focus on the lecture content and delivery, not the instructor personally.
- Avoid generic advice that could apply to any lecture.
- Every issue should be tied to a timestamp or a clearly observable pattern in the transcript.
- Prefer concrete improvements over broad criticism.

Lecture-type awareness:
First infer the lecture format from the transcript. It may be a programming demo, math explanation, science lecture, humanities lecture, slide-based lecture, whiteboard lecture, lab walkthrough, case discussion, or conceptual overview.

Then adapt the audit:
- For programming or technical demos, check whether syntax, inputs, outputs, errors, function behavior, and step-by-step reasoning are explained clearly.
- For math lectures, check whether symbols, formulas, assumptions, derivation steps, and problem-solving transitions are explained verbally.
- For science lectures, check whether mechanisms, diagrams, terminology, units, and cause-effect relationships are explained clearly.
- For humanities or social science lectures, check whether terms, historical context, claims, evidence, and interpretive transitions are clear.
- For business or case lectures, check whether frameworks, assumptions, tradeoffs, and decisions are explained with enough context.
- For slide-heavy lectures, check whether visual content is described rather than relying on phrases like "this slide" or "as you can see."
- For demo or lab lectures, check whether each action is explained before or during execution.

Accessibility guidance:
Accessibility means helping students access the content through multiple modes, including captions, audio-only review, screen readers, slower processing, and different levels of prior knowledge.

Do not recommend captions or transcripts unless the transcript is missing, poor, or unavailable.
Do not tell the instructor to "use screen readers."
Instead, focus on what the instructor can improve in the lecture itself.

Evaluate whether:
- Important visual information is described verbally.
- Technical terms and acronyms are defined before use.
- Symbols, formulas, code, charts, diagrams, or slides are explained in words.
- The lecture avoids vague references like "this," "that," "here," or "as you can see" without explanation.
- Students can follow the lecture through audio-only review or captions.
- Dense explanations include pauses, recaps, or examples.
- Instructions are stated clearly and sequentially.
- Examples are concrete enough for students with varied prior knowledge.

Equity and inclusion guidance:
Evaluate whether the lecture supports a broad range of learners.
Do not overclaim bias or exclusion unless the transcript supports it.

Look for:
- Assumed prior knowledge that may leave some students behind.
- Jokes, analogies, or examples that may confuse students from different backgrounds.
- Opportunities to normalize confusion and invite participation.
- Whether examples are broadly understandable.
- Whether the instructor provides multiple ways into the concept.

Pedagogical clarity guidance:
Evaluate whether the lecture:
- Defines key concepts before using them.
- Explains why the topic matters.
- Moves from simple to complex ideas.
- Uses examples after abstract explanations.
- Makes transitions clear.
- Summarizes important ideas.
- Connects new content to prior knowledge.

Structure and pacing guidance:
Evaluate whether the lecture:
- Has a clear opening.
- Previews what students will learn.
- Signals transitions.
- Gives students time to process difficult ideas.
- Avoids long dense explanation blocks.
- Ends with a useful recap or next step.

Cognitive load guidance:
Identify where the lecture introduces too many ideas at once.
Suggest how to split, sequence, recap, or simplify those sections.

Student engagement guidance:
Suggest opportunities for:
- Reflection questions
- Checks for understanding
- Short pauses
- Prediction prompts
- Examples
- Mini-recaps
- Practice moments

Rewrite guidance:
For timestamped suggested rewrites:
- Keep the instructor's likely intent.
- Make the rewrite clearer, more accessible, or better structured.
- Do not change the subject matter.
- Do not make the instructor sound unnatural.
- Make rewrites realistic enough to say in a lecture.

If you identify an analogy as confusing, the suggested rewrite should replace it with a clearer subject-relevant example, not restate the same analogy.

Return valid JSON only.
"""

FACULTY_AUDIT_JSON_INSTRUCTIONS = """
Return JSON in this exact structure:

{
  "lecture_title": "string",
  "overall_summary": "string",
  "highest_impact_fix": {
    "timestamp": "MM:SS",
    "issue": "string",
    "why_it_matters": "string",
    "suggested_improvement": "string"
  },
  "priority_fixes": [
    {
      "priority": "High",
      "timestamp": "MM:SS",
      "issue": "string",
      "why_it_matters": "string",
      "suggested_improvement": "string"
    }
  ],
  "pedagogical_clarity": {
    "summary": "string",
    "strengths": ["string"],
    "opportunities": ["string"]
  },
  "accessibility": {
    "summary": "string",
    "strengths": ["string"],
    "opportunities": ["string"]
  },
  "equity_and_inclusion": {
    "summary": "string",
    "strengths": ["string"],
    "opportunities": ["string"]
  },
  "structure_and_pacing": {
    "summary": "string",
    "strengths": ["string"],
    "opportunities": ["string"]
  },
  "cognitive_load": {
    "summary": "string",
    "strengths": ["string"],
    "opportunities": ["string"]
  },
  "student_engagement": {
    "summary": "string",
    "strengths": ["string"],
    "opportunities": ["string"]
  },
  "timestamped_rewrites": [
    {
      "timestamp": "MM:SS",
      "current_issue": "string",
      "suggested_rewrite": "string",
      "why_this_helps": "string"
    }
  ],
  "final_notes": "string"
}

Rules:
- Include 3 to 5 priority fixes.
- Include 5 to 8 timestamped rewrites.
- At least one priority fix should address student understanding.
- At least one rewrite should improve clarity, accessibility, or pacing.
- The highest impact fix should be the single most useful change before publishing.
- Do not include markdown outside the JSON.
- Do not include comments in the JSON.
- Do not give generic advice such as "add captions" unless the transcript evidence supports it.
- Do not claim a lecture has equity or accessibility problems unless the transcript supports the claim.
- If evidence is limited, say "insufficient evidence" inside the relevant field.
"""

def _seconds_to_timestamp(seconds_value) -> str:
    try:
        total_seconds = int(float(seconds_value))
    except (TypeError, ValueError):
        total_seconds = 0

    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def _safe_chunk_value(chunk, key: str, default=None):
    if isinstance(chunk, dict):
        return chunk.get(key, default)

    return getattr(chunk, key, default)


def format_transcript_for_audit(transcript_chunks) -> str:
    lines = []

    for chunk in transcript_chunks:
        text = (
            _safe_chunk_value(chunk, "text", "")
            or _safe_chunk_value(chunk, "content", "")
            or ""
        ).strip()

        if not text:
            continue

        start_time = _safe_chunk_value(chunk, "start_time", None)

        if start_time:
            timestamp = str(start_time)
        else:
            timestamp = _seconds_to_timestamp(_safe_chunk_value(chunk, "start", 0))

        lines.append(f"[{timestamp}] {text}")

    return "\n".join(lines)


def limit_transcript_for_audit(transcript_text: str, max_chars: int = 45000) -> str:
    """
    Keeps the faculty audit call from becoming too large.
    This still gives the model enough lecture content to identify patterns,
    timestamps, and rewrites.
    """

    if len(transcript_text) <= max_chars:
        return transcript_text

    head_chars = int(max_chars * 0.45)
    middle_chars = int(max_chars * 0.25)
    tail_chars = int(max_chars * 0.30)

    transcript_length = len(transcript_text)
    middle_start = max((transcript_length // 2) - (middle_chars // 2), 0)
    middle_end = middle_start + middle_chars

    return "\n".join(
        [
            transcript_text[:head_chars],
            "\n[Transcript shortened for audit: middle sample begins]\n",
            transcript_text[middle_start:middle_end],
            "\n[Transcript shortened for audit: ending sample begins]\n",
            transcript_text[-tail_chars:],
        ]
    )


def _as_string(value: Any, fallback: str) -> str:
    if value is None:
        return fallback

    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else fallback

    return str(value)


def _as_list(value: Any) -> list:
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]

    if isinstance(value, str) and value.strip():
        return [value.strip()]

    return []


def _normalize_dimension(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return {
            "summary": _as_string(
                value.get("summary"),
                "Insufficient evidence available.",
            ),
            "strengths": _as_list(value.get("strengths")),
            "opportunities": _as_list(value.get("opportunities")),
        }

    if isinstance(value, str):
        return {
            "summary": value,
            "strengths": [],
            "opportunities": [],
        }

    return {
        "summary": "Insufficient evidence available.",
        "strengths": [],
        "opportunities": [],
    }


def _normalize_highest_impact_fix(value: Any) -> Dict[str, str]:
    if isinstance(value, dict):
        return {
            "timestamp": _as_string(value.get("timestamp"), "00:00"),
            "issue": _as_string(value.get("issue"), "No specific issue identified."),
            "why_it_matters": _as_string(
                value.get("why_it_matters"),
                "This improvement may help students understand the lecture more clearly.",
            ),
            "suggested_improvement": _as_string(
                value.get("suggested_improvement"),
                "Add a clearer explanation, example, or transition at this point.",
            ),
        }

    if isinstance(value, str):
        return {
            "timestamp": "00:00",
            "issue": value,
            "why_it_matters": "This is the highest-impact improvement identified from the transcript.",
            "suggested_improvement": "Revise this part of the lecture with a clearer explanation and student-facing example.",
        }

    return {
        "timestamp": "00:00",
        "issue": "No specific issue identified.",
        "why_it_matters": "The model did not return a valid highest-impact fix.",
        "suggested_improvement": "Review the lecture transcript and add a clearer opening, transition, example, or recap.",
    }


def _normalize_priority_fixes(value: Any) -> list:
    if not isinstance(value, list):
        return []

    normalized = []

    for item in value:
        if not isinstance(item, dict):
            continue

        normalized.append(
            {
                "priority": _as_string(item.get("priority"), "Medium"),
                "timestamp": _as_string(item.get("timestamp"), "00:00"),
                "issue": _as_string(item.get("issue"), "No specific issue identified."),
                "why_it_matters": _as_string(
                    item.get("why_it_matters"),
                    "This may affect student understanding.",
                ),
                "suggested_improvement": _as_string(
                    item.get("suggested_improvement"),
                    "Clarify this section with a more direct explanation or example.",
                ),
            }
        )

    return normalized


def _normalize_rewrites(value: Any) -> list:
    if not isinstance(value, list):
        return []

    normalized = []

    for item in value:
        if not isinstance(item, dict):
            continue

        normalized.append(
            {
                "timestamp": _as_string(item.get("timestamp"), "00:00"),
                "current_issue": _as_string(
                    item.get("current_issue"),
                    "The current explanation may be unclear for some students.",
                ),
                "suggested_rewrite": _as_string(
                    item.get("suggested_rewrite"),
                    "Here is a clearer way to explain this concept.",
                ),
                "why_this_helps": _as_string(
                    item.get("why_this_helps"),
                    "This makes the explanation more direct and easier to follow.",
                ),
            }
        )

    return normalized


def normalize_faculty_audit_payload(
    payload: Dict[str, Any],
    lecture_title: str,
) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        payload = {}

    normalized = {
        "lecture_title": _as_string(
            payload.get("lecture_title"),
            lecture_title or "Untitled Lecture",
        ),
        "overall_summary": _as_string(
            payload.get("overall_summary"),
            "The audit could not produce a complete overall summary.",
        ),
        "highest_impact_fix": _normalize_highest_impact_fix(
            payload.get("highest_impact_fix")
        ),
        "priority_fixes": _normalize_priority_fixes(payload.get("priority_fixes")),
        "pedagogical_clarity": _normalize_dimension(
            payload.get("pedagogical_clarity")
        ),
        "accessibility": _normalize_dimension(payload.get("accessibility")),
        "equity_and_inclusion": _normalize_dimension(
            payload.get("equity_and_inclusion")
        ),
        "structure_and_pacing": _normalize_dimension(
            payload.get("structure_and_pacing")
        ),
        "cognitive_load": _normalize_dimension(payload.get("cognitive_load")),
        "student_engagement": _normalize_dimension(
            payload.get("student_engagement")
        ),
        "timestamped_rewrites": _normalize_rewrites(
            payload.get("timestamped_rewrites")
        ),
        "final_notes": _as_string(
            payload.get("final_notes"),
            "Use this private report as a practical guide for improving the lecture before publishing.",
        ),
    }

    if not normalized["priority_fixes"]:
        normalized["priority_fixes"] = [
            {
                "priority": "Medium",
                "timestamp": "00:00",
                "issue": "The audit did not return specific priority fixes.",
                "why_it_matters": "A prioritized fix list helps the instructor decide what to improve first.",
                "suggested_improvement": "Review the opening, transitions, examples, and recap for clarity.",
            }
        ]

    if not normalized["timestamped_rewrites"]:
        normalized["timestamped_rewrites"] = [
            {
                "timestamp": "00:00",
                "current_issue": "The audit did not return timestamped rewrites.",
                "suggested_rewrite": "Add a clearer explanation, then follow it with a concrete example students can connect to.",
                "why_this_helps": "Students learn more effectively when abstract ideas are paired with concrete examples.",
            }
        ]

    return normalized


def _default_dimension() -> AuditDimension:
    return AuditDimension(
        summary="Insufficient evidence available.",
        strengths=[],
        opportunities=[],
    )


def build_empty_faculty_audit_report(
    lecture_title: str,
    message: str,
) -> FacultyAuditReport:
    return FacultyAuditReport(
        lecture_title=lecture_title or "Untitled Lecture",
        overall_summary=message,
        highest_impact_fix=HighestImpactFix(
            timestamp="00:00",
            issue="No usable transcript was available for audit.",
            why_it_matters="The audit needs timestamped lecture content to provide grounded recommendations.",
            suggested_improvement="Try another public lecture URL with captions or use a video with clearer transcript availability.",
        ),
        priority_fixes=[
            PriorityFix(
                priority="Medium",
                timestamp="00:00",
                issue="Transcript unavailable.",
                why_it_matters="Without transcript evidence, the audit cannot produce grounded feedback.",
                suggested_improvement="Use a lecture with captions or paste a transcript-based workflow later.",
            )
        ],
        pedagogical_clarity=_default_dimension(),
        accessibility=_default_dimension(),
        equity_and_inclusion=_default_dimension(),
        structure_and_pacing=_default_dimension(),
        cognitive_load=_default_dimension(),
        student_engagement=_default_dimension(),
        timestamped_rewrites=[
            TimestampedRewrite(
                timestamp="00:00",
                current_issue="No transcript content was available.",
                suggested_rewrite="No rewrite can be generated without transcript evidence.",
                why_this_helps="Timestamped rewrites must be grounded in actual lecture content.",
            )
        ],
        final_notes="This private report could not be generated because the transcript was unavailable or empty.",
    )


def generate_faculty_audit(
    transcript_chunks,
    lecture_title: str = "Untitled Lecture",
) -> FacultyAuditReport:
    transcript_text = format_transcript_for_audit(transcript_chunks)

    if not transcript_text.strip():
        return build_empty_faculty_audit_report(
            lecture_title=lecture_title,
            message="No usable transcript was found for this lecture.",
        )

    transcript_text = limit_transcript_for_audit(transcript_text)

    user_prompt = f"""
Lecture title:
{lecture_title or "Untitled Lecture"}

Transcript with timestamps:
{transcript_text}

Task:
Generate a private faculty lecture audit report.

Audit dimensions:
1. Pedagogical clarity
2. Accessibility
3. Equity and inclusion
4. Structure and pacing
5. Cognitive load
6. Student engagement

Important:
- This is private feedback for the instructor.
- This is not surveillance.
- This is not an evaluation of the instructor.
- Be constructive and specific.
- Give timestamped suggested rewrites.

{FACULTY_AUDIT_JSON_INSTRUCTIONS}
"""

    audit_payload = generate_json(
        system_prompt=FACULTY_AUDIT_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    normalized_payload = normalize_faculty_audit_payload(
        payload=audit_payload,
        lecture_title=lecture_title,
    )

    return FacultyAuditReport(**normalized_payload)