# LectureForge AI Frontend

React + Tailwind frontend for the LectureForge AI backend.

## Setup

```bash
cd lectureforge-frontend
npm install
cp .env.example .env
npm run dev
```

Open:

```txt
http://localhost:5173
```

Make sure the backend is running at:

```txt
http://localhost:8000
```

## Backend endpoints used

- `POST /process-video`
- `GET /job-status/{job_id}`
- `GET /study-kit/{job_id}`
- `POST /search`

## Features

- YouTube URL input
- Agent progress polling
- Timestamped outline
- Three-level summaries
- Flip flashcards
- React Flow concept map
- Semantic search
- Full transcript viewer
