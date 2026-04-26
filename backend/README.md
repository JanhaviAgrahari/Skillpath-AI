# AI-Powered Skill Assessment Backend

FastAPI backend scaffold for the hackathon project. This backend is structured for a session-based, agentic workflow that supports:

- resume and JD intake
- skill extraction and gap analysis
- conversational assessment
- personalized learning plan generation
- summary and export

## Tech Stack

- FastAPI
- Uvicorn
- Supabase PostgreSQL
- SQLAlchemy
- asyncpg
- Gemini API

## Project Structure

```text
backend/
├─ app/
│  ├─ api/
│  ├─ core/
│  ├─ db/
│  ├─ models/
│  ├─ prompts/
│  ├─ schemas/
│  ├─ services/
│  └─ utils/
├─ sample_data/
├─ tests/
├─ .env.example
├─ .gitignore
├─ Dockerfile
├─ pytest.ini
├─ requirements.txt
└─ README.md
```

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` with the values you need. For a quick local run, only `GEMINI_API_KEY` is optional because the backend falls back to deterministic behavior.

## Environment Variables

Core:
- `APP_NAME`
- `APP_ENV`
- `APP_DEBUG`
- `API_V1_PREFIX`
- `HOST`
- `PORT`
- `CORS_ORIGINS`

LLM:
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `LLM_TIMEOUT_SECONDS`
- `LLM_MAX_RETRIES`

Database:
- `SUPABASE_DB_HOST`
- `SUPABASE_DB_PORT`
- `SUPABASE_DB_NAME`
- `SUPABASE_DB_USER`
- `SUPABASE_DB_PASSWORD`
- `SUPABASE_DB_SSLMODE`

## Run

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You can also use the configured env vars:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Tests

```bash
cd backend
pytest
```

The test suite uses the in-memory session store and sample files under `sample_data/`, so it runs without external services.

## Sample Data

- `sample_data/payloads/` contains example resume and JD input payloads
- `sample_data/api/requests/` contains example request bodies
- `sample_data/api/responses/` contains example response payloads
- `sample_data/files/` contains a sample resume text file for local parsing tests

## Local Development Notes

- The current demo flow uses an in-memory session store for speed and reliability during the hackathon.
- Supabase-ready SQLAlchemy models are included, but persistent DB wiring is still the next integration step.
- If Gemini is unavailable, parsing, skill extraction, scoring, and planning still fall back to deterministic logic.

## Available Endpoints

- `GET /health`
- `GET /api/v1/health`
- `POST /api/v1/sessions`
- `GET /api/v1/sessions/{session_id}`
- `POST /api/v1/sessions/{session_id}/resume`
- `POST /api/v1/sessions/{session_id}/job-description`
- `POST /api/v1/sessions/{session_id}/analysis/run`
- `GET /api/v1/sessions/{session_id}/analysis`
- `GET /api/v1/sessions/{session_id}/analysis/complete`
- `POST /api/v1/sessions/{session_id}/assessment/start`
- `GET /api/v1/sessions/{session_id}/assessment`
- `POST /api/v1/sessions/{session_id}/assessment/answer`
- `POST /api/v1/sessions/{session_id}/assessment/complete`
- `POST /api/v1/sessions/{session_id}/learning-plan/generate`
- `GET /api/v1/sessions/{session_id}/learning-plan`
- `POST /api/v1/sessions/{session_id}/summary/generate`
- `GET /api/v1/sessions/{session_id}/summary`
- `GET /api/v1/sessions/{session_id}/export`
- `POST /api/v1/workflow/orchestrate`

Resume intake, analysis, assessment, learning-plan generation, final report export, and workflow orchestration now return structured backend payloads. The current implementation is designed for fast hackathon iteration, with in-memory session state, centralized error handling, and deterministic fallback logic when Gemini is unavailable.

## Deployment

Build and run with Docker:

```bash
cd backend
docker build -t ai-skill-backend .
docker run --rm -p 8000:8000 --env-file .env ai-skill-backend
```

## Notes

- Authentication is intentionally omitted for the hackathon MVP.
- Session handling is UUID-based.
- Session state currently resets on server restart because the runtime store is in memory.
- Gemini structured output is used when `GEMINI_API_KEY` is configured; otherwise deterministic fallback logic is used.
- SQLAlchemy models and async DB session setup are included for the later Supabase persistence step.
