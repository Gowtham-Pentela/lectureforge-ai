# LectureForge AI

LectureForge AI turns a single YouTube lecture URL into an interactive study environment for students.

A student can paste a lecture video link and instantly generate a structured outline, multi-depth summaries, timestamped flashcards, semantic search, transcript view, concept map, and multilingual study materials.

The app is designed for students who missed a lecture, need to review quickly before an exam, or want to study in short focused bursts instead of rewatching a full lecture passively.

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

##  Features

###  YouTube URL to Study Kit

Students paste a YouTube lecture URL and LectureForge processes the lecture into a complete study environment.

```text
YouTube URL -> Transcript -> Lecture Analysis -> Study Kit -> Interactive UI
````

---

###  Timestamped Outline

LectureForge generates a structured outline of the lecture with start and end timestamps.

Each outline section includes an **Open at timestamp** button that jumps directly back to the exact moment in the YouTube video.

Example:

```text
00:03:31 - 00:04:35
Copying Arrays Properly
Open at 00:03:31
```

---

###  Multi-Depth Summaries

The app generates plain-language summaries at multiple depths:

* 90-second summary
* 5-minute summary
* Full summary

This helps students choose how deeply they want to review based on the time they have.

---

###  Flashcards With Source Moments

LectureForge creates flashcards from the lecture content.

Each flashcard includes:

* Question
* Answer
* Source timestamp
* Link back to the exact video moment

This makes the flashcards grounded in the original lecture instead of being generic study questions.

---

###  Semantic Search

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

###  Bilingual Study Support

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

###  Progressive Translation

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

###  Concept Map

The app generates a visual concept map showing how major lecture topics connect.

This helps students understand the structure of the lecture at a glance.

---

##  Architecture

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
  v
Agent 3: Study Kit Generation
  |
  v
Semantic Search Index
  |
  v
React Study Dashboard
```

---

##  Agent Workflow

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

##  Search Design

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

##  Translation Design

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

##  Tech Stack

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

##  Project Structure

```text
lectureforge-ai/
├── lectureforge-backend/
│   ├── agents/
│   │   ├── agent1_ingestion.py
│   │   ├── agent2_analysis.py
│   │   └── agent3_study.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── job_store.py
│   │   └── openai_service.py
│   ├── utils/
│   │   ├── transcript_utils.py
│   │   └── study_kit_validator.py
│   ├── main.py
│   └── requirements.txt
│
└── lectureforge-frontend/
    ├── src/
    │   ├── components/
    │   │   ├── VideoForm.jsx
    │   │   ├── ProgressCard.jsx
    │   │   ├── StudyDashboard.jsx
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

##  Getting Started Locally

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

##  Demo Flow

1. Start backend on port `8000`
2. Start frontend on port `5173`
3. Paste a YouTube lecture URL
4. Click **Generate Study Kit**
5. Wait for processing to complete
6. Explore:

   * Outline
   * Summaries
   * Flashcards
   * Concept Map
   * Search
   * Transcript
7. Click timestamp jump links to open the lecture at exact moments
8. Change display language to translate the study kit progressively

---

##  Environment Variables

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

## ☁️ Deployment

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

##  Current Limitations

* Jobs are stored in memory, so job state can be lost if the backend restarts.
* For production, Redis, Supabase, or PostgreSQL should replace the in-memory job store.
* Search embeddings are generated from the English transcript for efficiency.
* Translated search queries are converted back to English before semantic search.
* Supadata is used for transcript extraction in deployment because direct YouTube caption access can be blocked from cloud IPs.

---

##  Future Improvements

* Persistent job storage with Redis, Supabase, or PostgreSQL
* User accounts and saved study kits
* Export study kits to PDF
* Export flashcards to Anki
* Quiz mode
* Notes mode
* Institution dashboard
* Video player embedded directly in the app
* More granular transcript chunk translation
* Evaluation dashboard for transcript quality and answer grounding

---

## Why This Matters

Students often do not have time to rewatch full lecture videos. LectureForge AI helps them convert passive lecture content into active study material.

With timestamped jump-points, semantic search, flashcards, and multilingual support, a student can review a 60-minute lecture in a focused 15-minute study session while still staying grounded in the original source.

---

##  Final Demo Statement

LectureForge AI lets a student paste one lecture YouTube URL and turns it into an interactive study environment with timestamped outline jump-points, multi-depth summaries, flashcards tied to cited source moments, semantic search that jumps back to the exact lecture moment, transcript view, concept map, and progressive multilingual translation without reprocessing the video.

````

