
# LectureForge AI

LectureForge AI turns a single YouTube lecture URL into an interactive learning and lecture-improvement workspace.

The app supports two modes:

1. **Student Study Mode**  
   Students paste a lecture video link and generate a structured study kit with outlines, summaries, flashcards, concept maps, semantic search, transcript view, and multilingual study support.

2. **Faculty Audit Mode**  
   Faculty paste a lecture video link and generate a private, instructor-facing audit across pedagogy, accessibility, equity, clarity, pacing, cognitive load, and student engagement. The report includes a prioritized fix list and timestamped suggested rewrites.

## Live Demo

Try LectureForge AI here:

```
https://lectureforge-ai.vercel.app/ 
```

LectureForge AI is designed for students who want to study efficiently and faculty who want private, practical feedback before publishing or improving a lecture.

---

## Student Capability

LectureForge AI helps students compress long lecture videos into active, targeted study sessions.

### What the student can do

- Paste one YouTube lecture URL
- Generate a structured study kit
- Review a timestamped outline
- Jump back to exact moments in the original video
- Read summaries at multiple depths
- Practice with flashcards tied to source moments
- Search the lecture semantically using natural language
- Translate study materials into multiple languages
- Study from the transcript, concept map, summaries, flashcards, and search results

---

## Faculty Capability

LectureForge AI also helps faculty improve lectures before publishing or reuse existing lecture recordings more effectively.

Faculty Audit Mode generates a private, instructor-facing report. It is voluntary, private, and explicitly not a surveillance or evaluation tool.

### What the faculty member can do

- Paste one YouTube lecture URL
- Generate a private lecture audit
- Review the single highest-impact fix before publishing
- See a prioritized list of improvements
- Audit the lecture across:
  - Pedagogical clarity
  - Accessibility
  - Equity and inclusion
  - Structure and pacing
  - Cognitive load
  - Student engagement
- Review timestamped suggested rewrites
- Identify unclear explanations, rushed transitions, and missing recaps
- Improve lecture clarity before students see the final version

### Faculty report includes

- Overall lecture summary
- Highest-impact fix
- Priority fix list
- Pedagogical clarity feedback
- Accessibility feedback
- Equity and inclusion feedback
- Structure and pacing feedback
- Cognitive load feedback
- Student engagement feedback
- Timestamped suggested rewrites
- Final instructor notes

### Faculty privacy principle

Faculty Audit Mode is designed to support lecture improvement, not faculty monitoring.

It does not produce instructor scores, rankings, grades, or performance labels. The report is written as private, constructive feedback for the instructor.

---

## Features

### YouTube URL to Study Kit

Students paste a YouTube lecture URL and LectureForge processes the lecture into a complete study environment.

```text
YouTube URL -> Transcript -> Lecture Analysis -> Study Kit -> Interactive UI
````

---

### YouTube URL to Faculty Audit

Faculty paste a YouTube lecture URL and LectureForge generates a private audit report.

```text
YouTube URL -> Transcript -> Lecture Analysis -> Faculty Audit -> Private Report UI
```

---

### Timestamped Outline

LectureForge generates a structured outline of the lecture with start and end timestamps.

Each outline section includes an **Open at timestamp** button that jumps directly back to the exact moment in the YouTube video.

Example:

```text
00:03:31 - 00:04:35
Copying Arrays Properly
Open at 00:03:31
```

---

### Multi-Depth Summaries

The app generates plain-language summaries at multiple depths:

* 90-second summary
* 5-minute summary
* Full summary

This helps students choose how deeply they want to review based on the time they have.

---

### Flashcards With Source Moments

LectureForge creates flashcards from the lecture content.

Each flashcard includes:

* Question
* Answer
* Source timestamp
* Link back to the exact video moment

This makes the flashcards grounded in the original lecture instead of being generic study questions.

---

### Semantic Search

Students can type any question or topic, and LectureForge finds the most relevant lecture moments.

Example query:

```text
How do you copy an array in Python?
```

The app returns matching transcript chunks with:

* Timestamp
* Relevance score
* Transcript snippet
* Open at timestamp link

This allows students to locate the exact part of the lecture that answers their question.

---

### Bilingual Study Support

LectureForge generates English study materials by default.

Students can then translate the generated study kit into other languages without reprocessing the video.

Supported languages currently include:

* English
* Hindi
* Telugu
* Spanish
* French
* Arabic
* Urdu

---

### Progressive Translation

Instead of waiting for the entire study kit to translate at once, LectureForge translates section by section.

Translation order:

1. Title
2. Outline
3. Summaries
4. Key concepts
5. Flashcards
6. Concept map
7. Transcript chunks in batches

This improves perceived speed and lets students start reading translated sections immediately.

---

### Concept Map

The app generates a visual concept map showing how major lecture topics connect.

This helps students understand the structure of the lecture at a glance.

---

### Private Faculty Audit

Faculty Audit Mode reviews the lecture from an instructional improvement perspective.

The audit focuses on:

* Whether key concepts are defined clearly
* Whether transitions are easy to follow
* Whether complex ideas are paced well
* Whether the lecture supports students with different levels of prior knowledge
* Whether visual, technical, or abstract content is explained clearly in words
* Whether students receive enough recaps, examples, and reflection points
* Whether the instructor can make one high-impact change before publishing

The output is private, constructive, and instructor-facing.

---

### Timestamped Suggested Rewrites

Faculty Audit Mode generates specific timestamped rewrites.

Example:

```text
00:03:35
Issue:
The filter function is introduced before its inputs and return behavior are clearly explained.

Suggested rewrite:
The filter function takes two arguments: a function that defines the condition and an iterable, such as a list. It returns only the elements that satisfy the condition.

Why this helps:
This gives students a clear mental model before they see the code example.
```

---

## Architecture

LectureForge AI uses a multi-agent backend pipeline.

```text
Frontend
  |
  | YouTube URL
  v
FastAPI Backend
  |
  v
Agent 1: Transcript Ingestion
  |
  v
Agent 2: Lecture Structure Analysis
  |
  +-----------------------------+
  |                             |
  v                             v
Agent 3: Study Kit Generation   Agent 4: Faculty Audit Generation
  |                             |
  v                             v
Semantic Search Index           Private Faculty Report
  |                             |
  v                             v
React Study Dashboard           React Faculty Audit Dashboard
```
img src = 'lectureforge_architecture_diagram.png'
---

## Agent Workflow

### Agent 1: Transcript Ingestion

Agent 1 extracts the lecture transcript.

Current ingestion strategy:

1. Supadata transcript API
2. youtube-transcript-api fallback
3. yt-dlp captions fallback
4. Whisper audio transcription fallback

Supadata is used first in deployment because cloud platforms like Render can be blocked by YouTube when trying to fetch captions directly.

---

### Agent 2: Lecture Analysis

Agent 2 analyzes the transcript and identifies:

* Lecture title
* Major sections
* Timestamped outline
* Key concepts
* Source moments

This title and structure are used by both Student Study Mode and Faculty Audit Mode.

---

### Agent 3: Study Kit Generation

Agent 3 generates:

* Short summary
* Medium summary
* Full summary
* Flashcards
* Concept map
* Search-ready transcript chunks

---

### Agent 4: Faculty Audit Generation

Agent 4 generates a private instructor-facing audit.

It reviews the lecture across:

* Pedagogical clarity
* Accessibility
* Equity and inclusion
* Structure and pacing
* Cognitive load
* Student engagement

It returns:

* Highest-impact fix
* Prioritized fixes
* Dimension-by-dimension feedback
* Timestamped suggested rewrites
* Final instructor notes

Agent 4 does not score, rank, or evaluate the instructor. It focuses on practical lecture improvement.

---

## Search Design

LectureForge creates embeddings from the English transcript chunks.

Search flow:

```text
User query -> Query embedding -> Similarity search -> Relevant transcript chunks
```

For translated study modes:

```text
Translated query -> English query -> English semantic search -> Translated result display
```

This keeps the search index efficient while still supporting multilingual users.

---

## Translation Design

The video is processed once in English.

When the student changes language, LectureForge does not reprocess the lecture. Instead, it translates the already generated study kit section by section.

```text
English Study Kit
  |
  | User selects language
  v
Translate title
Translate outline
Translate summaries
Translate flashcards
Translate concept map
Translate transcript batches
```

Translated sections are cached in memory for faster switching during the same session.

---

## Faculty Audit Design

Faculty Audit Mode uses the same transcript ingestion and lecture analysis pipeline as Student Study Mode.

```text
YouTube URL
  |
  v
Transcript extraction
  |
  v
Lecture title and structure analysis
  |
  v
Private faculty audit generation
  |
  v
Faculty Audit Dashboard
```

The audit prompt is designed to work across different lecture types, including:

* Programming lectures
* Math lectures
* Science lectures
* Humanities lectures
* Business lectures
* Slide-based lectures
* Whiteboard lectures
* Demo or lab walkthroughs
* Conceptual overview lectures

The audit adapts feedback based on the lecture type instead of using a one-size-fits-all rubric.

---

## Tech Stack

### Frontend

* React
* Vite
* Tailwind CSS
* React Flow
* Lucide React

### Backend

* FastAPI
* OpenAI API
* Supadata Transcript API
* youtube-transcript-api
* yt-dlp
* NumPy
* Pydantic

### Deployment

* Frontend: Vercel
* Backend: Render

---

## Project Structure

```text
lectureforge-ai/
├── lectureforge-backend/
│   ├── agents/
│   │   ├── agent1_ingestion.py
│   │   ├── agent2_analysis.py
│   │   ├── agent3_study.py
│   │   └── agent4_faculty_audit.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── job_store.py
│   │   └── openai_service.py
│   ├── utils/
│   │   ├── transcript_utils.py
│   │   ├── study_kit_validator.py
│   │   └── faculty_audit_validator.py
│   ├── main.py
│   └── requirements.txt
│
└── lectureforge-frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Header.jsx
    │   │   ├── VideoForm.jsx
    │   │   ├── ProgressCard.jsx
    │   │   ├── StudyDashboard.jsx
    │   │   ├── FacultyAuditDashboard.jsx
    │   │   ├── OutlineTab.jsx
    │   │   ├── SummariesTab.jsx
    │   │   ├── FlashcardsTab.jsx
    │   │   ├── ConceptMapTab.jsx
    │   │   ├── SearchTab.jsx
    │   │   └── TranscriptTab.jsx
    │   ├── lib/
    │   │   └── api.js
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

---

## Getting Started Locally

### 1. Clone the repository

```bash
git clone https://github.com/Gowtham-Pentela/lectureforge-ai.git
cd lectureforge-ai
```

---

## Backend Setup

### 2. Create backend environment file

Create:

```text
lectureforge-backend/.env
```

Add:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

SUPADATA_API_KEY=your_supadata_api_key_here
```

---

### 3. Install backend dependencies

```bash
cd lectureforge-backend
python3 -m pip install -r requirements.txt
```

---

### 4. Run backend

```bash
python3 -m uvicorn main:app --reload --port 8000
```

Backend runs at:

```text
http://localhost:8000
```

FastAPI docs:

```text
http://localhost:8000/docs
```

---

## Frontend Setup

### 5. Create frontend environment file

Create:

```text
lectureforge-frontend/.env
```

Add:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

### 6. Install frontend dependencies

```bash
cd ../lectureforge-frontend
npm install
```

---

### 7. Run frontend

```bash
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

---

## Demo Flow

### Student Study Mode

1. Start backend on port `8000`
2. Start frontend on port `5173`
3. Select **Student Study Mode**
4. Paste a YouTube lecture URL
5. Click **Generate Study Kit**
6. Wait for processing to complete
7. Explore:

   * Outline
   * Summaries
   * Flashcards
   * Concept Map
   * Search
   * Transcript
8. Click timestamp jump links to open the lecture at exact moments
9. Change display language to translate the study kit progressively

---

### Faculty Audit Mode

1. Start backend on port `8000`
2. Start frontend on port `5173`
3. Select **Faculty Audit Mode**
4. Paste a YouTube lecture URL
5. Click **Generate Faculty Audit**
6. Wait for processing to complete
7. Review:

   * Highest-impact fix
   * Priority fix list
   * Pedagogical clarity feedback
   * Accessibility feedback
   * Equity and inclusion feedback
   * Structure and pacing feedback
   * Cognitive load feedback
   * Student engagement feedback
   * Timestamped suggested rewrites
8. Use the report as private lecture-improvement guidance before publishing

---

## API Endpoints

### Student Study Mode

Start video processing:

```http
POST /process-video
```

Check job status:

```http
GET /job-status/{job_id}
```

Fetch generated study kit:

```http
GET /study-kit/{job_id}
```

Translate full study kit:

```http
POST /translate-study-kit
```

Translate one section:

```http
POST /translate-section
```

Search study kit:

```http
POST /search
```

---

### Faculty Audit Mode

Start faculty audit:

```http
POST /process-faculty-audit
```

Check job status:

```http
GET /job-status/{job_id}
```

Fetch faculty audit:

```http
GET /faculty-audit/{job_id}
```

Example:

```bash
curl -X POST http://localhost:8000/process-faculty-audit \
  -H "Content-Type: application/json" \
  -d '{"youtube_url":"https://www.youtube.com/watch?v=YOUR_VIDEO_ID"}'
```

Then fetch the result:

```bash
curl -s http://localhost:8000/faculty-audit/YOUR_JOB_ID | python3 -m json.tool
```

---

## Environment Variables

### Backend

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
SUPADATA_API_KEY=
```

### Frontend

```env
VITE_API_BASE_URL=http://localhost:8000
```

For production frontend deployment:

```env
VITE_API_BASE_URL=https://your-render-backend-url.onrender.com
```

---

## Deployment

### Backend on Render

Recommended Render settings:

```text
Root Directory: lectureforge-backend
Build Command: pip install -r requirements.txt
Start Command: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

Add environment variables in Render:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
SUPADATA_API_KEY=your_supadata_api_key_here
```

---

### Frontend on Vercel

Recommended Vercel settings:

```text
Framework Preset: Vite
Root Directory: lectureforge-frontend
Build Command: npm run build
Output Directory: dist
```

Add environment variable:

```env
VITE_API_BASE_URL=https://your-render-backend-url.onrender.com
```

---

## Current Limitations

* Jobs are stored in memory, so job state can be lost if the backend restarts.
* For production, Redis, Supabase, or PostgreSQL should replace the in-memory job store.
* Search embeddings are generated from the English transcript for efficiency.
* Translated search queries are converted back to English before semantic search.
* Faculty audit reports are generated from transcript evidence, so transcript quality affects audit quality.
* Supadata is used for transcript extraction in deployment because direct YouTube caption access can be blocked from cloud IPs.

---

## Future Improvements

* Persistent job storage with Redis, Supabase, or PostgreSQL
* User accounts and saved study kits
* Saved private faculty audit history
* Export study kits to PDF
* Export faculty audit reports to PDF
* Export flashcards to Anki
* Quiz mode
* Notes mode
* Embedded video player
* Clickable timestamp links inside Faculty Audit rewrites
* More granular transcript chunk translation
* Evaluation dashboard for transcript quality and answer grounding
* Faculty-side revision checklist based on priority fixes

---

## Why This Matters

Students often do not have time to rewatch full lecture videos. LectureForge AI helps them convert passive lecture content into active study material.

Faculty also rarely receive timely, specific feedback before publishing a lecture. Peer review is limited, and student evaluations arrive late and can reflect bias rather than instructional quality.

LectureForge AI supports both sides of the learning loop:

* Students get faster, more active study support.
* Faculty get private, practical feedback to improve lecture clarity before students rely on the material.

With timestamped jump-points, semantic search, flashcards, multilingual support, and private faculty audits, LectureForge turns lecture videos into useful learning infrastructure.

---

```
