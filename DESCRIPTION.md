# LectureForge AI — Description

## About

> Turn a YouTube lecture into a study kit and a private faculty audit.

LectureForge AI is an AI-powered learning and lecture-improvement workspace. It takes a single YouTube lecture URL and turns it into two complementary outputs:

### For students — a structured study kit

- Timestamped outline with one-click jumps back to the exact moment in the original video
- Multi-depth summaries (90-second, 5-minute, full)
- Flashcards anchored to source moments in the lecture
- Concept map showing how major topics connect
- Semantic search over the transcript using natural language
- Multilingual study support (English, Hindi, Telugu, Spanish, French, Arabic, Urdu) with progressive, section-by-section translation

### For faculty — a private, instructor-facing audit

- The single highest-impact fix before publishing
- A prioritized fix list
- Dimension-by-dimension feedback across pedagogy, accessibility, equity, structure and pacing, cognitive load, and student engagement
- Timestamped suggested rewrites for unclear explanations, rushed transitions, and missing recaps
- Designed as voluntary, private, constructive feedback — not a surveillance or evaluation tool

## How it works

```text
YouTube URL
  -> Transcript ingestion (captions, yt-dlp fallback, optional Whisper)
  -> Lecture structure analysis
  -> Study Kit  ->  Student Dashboard
  -> Faculty Audit  ->  Private Faculty Report
```

A four-agent pipeline runs on a FastAPI backend: transcript ingestion, lecture analysis, study kit generation, and faculty audit generation. The React + Vite frontend renders two dashboards — one for students, one for faculty.

## Tech stack

- **Backend:** FastAPI, OpenAI API, youtube-transcript-api, yt-dlp, NumPy, Pydantic
- **Frontend:** React, Vite, Tailwind CSS, React Flow, Lucide React
- **Deployment:** Vercel (frontend), Render (backend)
- **Mobile:** Capacitor (iOS + Android scaffolding)

## Why it matters

Students rarely have time to rewatch full lecture videos. Lecture also rarely receives timely, specific feedback before it's published. LectureForge AI supports both sides of the learning loop: students get faster, more active study support; faculty get private, practical feedback to improve lecture clarity before students rely on the material.

## Links

- **Live demo:** https://lectureforge-ai.vercel.app
- **Repository:** https://github.com/Gowtham-Pentela/lectureforge-ai
- **Mobile release checklist:** see [`MOBILE_RELEASE.md`](MOBILE_RELEASE.md)
- **Version notes:** see [`VERSION_NOTES.md`](VERSION_NOTES.md)
