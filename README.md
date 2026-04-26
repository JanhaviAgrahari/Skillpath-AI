# Skillpath — AI-Powered Skill Assessment & Learning Platform

An agentic AI application that assesses a candidate's skill proficiency against a target job description through a real-time, LLM-driven conversational interview. It identifies skill gaps, generates a personalized learning roadmap, and produces a detailed assessment report.

## Architecture

```
deccan_ai/
├── backend/          # FastAPI + Python (REST API, Gemini LLM integration)
│   ├── app/
│   │   ├── api/v1/   # Route handlers
│   │   ├── core/     # Config, exceptions, logging
│   │   ├── prompts/  # LLM prompt templates
│   │   ├── schemas/  # Pydantic request/response models
│   │   ├── services/ # Business logic (assessment, analysis, planning)
│   │   └── utils/    # Scoring, skill catalog, text normalization
│   └── requirements.txt
├── frontend/         # React + Vite + TailwindCSS
│   └── src/
│       ├── Landing.jsx     # Resume & JD input
│       ├── Workspace.jsx   # Conversational assessment chat
│       ├── Analysis.jsx    # Skill gap analysis dashboard
│       ├── Plan.jsx        # Week-by-week learning roadmap
│       └── Summary.jsx     # Final assessment report
└── README.md
```

## Key Features

- **Agentic Assessment** — Gemini conducts a multi-turn conversational interview, dynamically adapting questions based on the candidate's responses
- **Skill Gap Analysis** — LLM-powered extraction and comparison of resume skills vs. job requirements
- **Adaptive Follow-ups** — The AI probes deeper on shallow answers and moves on when confident
- **Learning Roadmap** — Auto-generated week-by-week plan prioritizing the most critical gaps
- **Assessment Report** — Exportable summary with per-skill scores and proficiency levels

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, Pydantic v2 |
| Frontend | React 19, Vite, TailwindCSS |
| LLM | Google Gemini (`gemini-2.5-flash-lite`) via `google-genai` SDK |
| State | In-memory session store (no database required for local dev) |

---

## Local Setup

### Prerequisites

- **Python 3.12+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **Google Gemini API Key** — [Get one here](https://aistudio.google.com/apikey)

### 1. Clone the Repository

```bash
git clone <repo-url>
cd deccan_ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv aienv

# Activate it
# Windows:
.\aienv\Scripts\activate
# macOS/Linux:
source aienv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
# Then edit .env and add your Gemini API key:
#   GEMINI_API_KEY=your_actual_key_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Start the Application

Open **two terminals**:

**Terminal 1 — Backend** (from `backend/` directory):
```bash
# Activate venv first if not already active
.\aienv\Scripts\activate        # Windows
source aienv/bin/activate        # macOS/Linux

uvicorn app.main:app --reload
```
Backend runs on: `http://localhost:8000`

**Terminal 2 — Frontend** (from `frontend/` directory):
```bash
npm run dev
```
Frontend runs on: `http://localhost:5173`

### 5. Use the App

1. Open `http://localhost:5173` in your browser
2. Paste your **resume text** on the left and the **job description** on the right
3. Click **Start Assessment** — the AI will begin an interactive interview
4. Answer the questions — the AI adapts in real time
5. Navigate to **Analyse** to see your skill gap matrix
6. Navigate to **Plan** to get a personalized learning roadmap
7. Navigate to **Report** for a downloadable summary

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sessions` | Create a new session |
| POST | `/api/v1/sessions/{id}/resume` | Submit resume text |
| POST | `/api/v1/sessions/{id}/job-description` | Submit job description |
| POST | `/api/v1/sessions/{id}/analysis/run` | Run skill gap analysis |
| GET | `/api/v1/sessions/{id}/analysis/complete` | Get full analysis results |
| POST | `/api/v1/sessions/{id}/assessment/start` | Start the AI assessment |
| GET | `/api/v1/sessions/{id}/assessment` | Get current assessment state |
| POST | `/api/v1/sessions/{id}/assessment/answer` | Submit an answer |
| POST | `/api/v1/sessions/{id}/assessment/complete` | Complete the assessment |
| POST | `/api/v1/sessions/{id}/learning-plan/generate` | Generate learning plan |
| GET | `/api/v1/sessions/{id}/learning-plan` | Get generated plan |
| POST | `/api/v1/sessions/{id}/summary/generate` | Generate final summary |
| GET | `/api/v1/sessions/{id}/summary` | Get summary |

Full API docs available at `http://localhost:8000/docs` (Swagger UI) when the backend is running.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | **Required.** Your Google Gemini API key | — |
| `GEMINI_MODEL` | Gemini model to use | `gemini-2.5-flash-lite` |
| `LLM_TIMEOUT_SECONDS` | Max seconds to wait for LLM response | `60` |
| `LLM_MAX_RETRIES` | Number of retries on LLM failure | `2` |
| `CORS_ORIGINS` | Allowed frontend origins (JSON array) | `["http://localhost:3000", "http://localhost:5173"]` |

---

## Project Flow

```
Resume + JD → Skill Extraction (LLM) → Gap Analysis
                                           ↓
                              Conversational Assessment (LLM)
                                           ↓
                              Skill Scores + Proficiency Levels
                                           ↓
                              Learning Plan Generation
                                           ↓
                              Final Report & Export
```

## Team

Built for the **Deccan AI Hackathon 2026**.
