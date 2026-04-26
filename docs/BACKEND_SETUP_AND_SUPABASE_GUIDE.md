# Backend Setup And Supabase Guide

This guide explains:
- what you need to fill manually
- how to configure `.env`
- how to start the backend locally
- how to create a Supabase project for the first time
- how to connect Supabase details to this backend

Important note:
- the backend already includes Supabase-ready config, SQLAlchemy models, and async DB session setup
- the current hackathon runtime flow still uses an in-memory session store for active session progression
- that means the app runs right now without needing Supabase
- Supabase setup is still useful now because your environment is already prepared for the later persistence step

---

## 1. What You Need Installed First

Install these on your machine:

1. Python 3.11 or 3.12
2. pip
3. Git
4. Postman
5. Optional: Docker Desktop

To check Python:

```bash
python --version
```

If `python` does not work on Windows, try:

```bash
py --version
```

---

## 2. Go To The Backend Folder

Open terminal in the project root and run:

```bash
cd backend
```

---

## 3. Create Virtual Environment

### Windows PowerShell

```bash
python -m venv .venv
.venv\Scripts\activate
```

If `python` does not work:

```bash
py -3 -m venv .venv
.venv\Scripts\activate
```

When active, you should see something like:

```bash
(.venv)
```

---

## 4. Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI
- Uvicorn
- SQLAlchemy
- asyncpg
- Gemini SDK
- PDF/DOCX parsers
- pytest tools

---

## 5. Create The `.env` File

Copy the example file:

### Windows PowerShell

```bash
copy .env.example .env
```

Then open `.env` in VS Code or any editor and fill in values.

---

## 6. Fields To Fill In `.env`

Below is what each variable means.

### App settings

```env
APP_NAME=AI Skill Assessment Backend
APP_ENV=development
APP_DEBUG=true
API_V1_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000
```

Recommended local values:
- keep these as they are for now

### CORS

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

Use:
- `3000` if your frontend runs on React/Next dev server
- `5173` if your frontend runs on Vite

If needed later, add more origins separated by commas.

### Gemini

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
LLM_TIMEOUT_SECONDS=20
LLM_MAX_RETRIES=2
```

What to do:
- replace `your_gemini_api_key` with your real Gemini API key
- keep the model as is unless you want to change it

Important:
- if `GEMINI_API_KEY` is empty, the backend still works using deterministic fallback logic
- for the best demo quality, add the real key

### Supabase / Postgres

```env
SUPABASE_DB_HOST=localhost
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=postgres
SUPABASE_DB_SSLMODE=prefer
```

For now:
- these values can stay placeholder values if you are just running the current hackathon version locally

Later:
- replace them with your real Supabase Postgres connection values

### Logging

```env
LOG_LEVEL=INFO
```

Use:
- `INFO` for normal use
- `DEBUG` if you want more logs while debugging

---

## 7. How To Get Gemini API Key

1. Open Google AI Studio or Gemini developer console
2. Create or sign into your Google account
3. Generate an API key
4. Copy the key
5. Paste it into:

```env
GEMINI_API_KEY=your_real_key_here
```

---

## 8. How To Start Backend Locally

Run:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

If everything is working, the backend should start on:

```text
http://localhost:8000
```

Useful URLs:
- health check: `http://localhost:8000/health`
- docs: `http://localhost:8000/docs`

---

## 9. How To Use Swagger Docs Quickly

FastAPI provides automatic docs.

Open:

```text
http://localhost:8000/docs
```

You can:
- expand endpoints
- click `Try it out`
- enter request values
- run requests directly from browser

This is useful when you want a quick local test without Postman.

---

## 10. How To Run Tests

Run:

```bash
pytest
```

This uses:
- in-memory session state
- local sample payloads
- no external DB needed

---

## 11. First-Time Supabase Setup

This section is written for a first-time Supabase user.

### Step 1: Create Supabase account

1. Go to [Supabase](https://supabase.com/)
2. Click `Start your project`
3. Sign in using GitHub, Google, or email

### Step 2: Create new project

1. Click `New project`
2. Choose your organization
3. Enter a project name
   - example: `ai-skill-assessment`
4. Set a strong database password
   - save this password somewhere safe
5. Choose a region close to you
6. Click `Create new project`

Wait for the project to finish provisioning.

### Step 3: Open project settings

Inside Supabase:

1. Open your project
2. Go to `Project Settings`
3. Open `Database`

You will find the connection details there.

### Step 4: Copy database connection values

Look for fields such as:
- host
- port
- database name
- user
- password
- SSL mode

Then fill them into your `.env`.

Example:

```env
SUPABASE_DB_HOST=db.xxxxxxxxx.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your_supabase_db_password
SUPABASE_DB_SSLMODE=require
```

### Step 5: Optional API keys

If you also want frontend-to-Supabase direct features later, you can collect:
- project URL
- anon public key
- service role key

But for the current backend code, the main thing you need is the Postgres database connection info.

### Step 6: Test that config is saved

After updating `.env`, restart the backend.

Important honesty note:
- the current backend codebase is prepared for Supabase-backed persistence
- but the main workflow still uses in-memory session state right now
- so setting Supabase values does not yet change session persistence behavior until DB integration is fully wired into the runtime services

That means:
- Supabase setup is ready and useful for the next persistence step
- the backend still runs fine now even before that final integration

---

## 12. How To Start Backend For Now

For the current hackathon version, the simplest working setup is:

1. create `.venv`
2. install requirements
3. copy `.env.example` to `.env`
4. add Gemini key if available
5. run:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

This is enough to:
- upload resume and JD
- run skill analysis
- run assessment
- generate learning plan
- generate summary
- use orchestration endpoint
- run tests

---

## 13. Optional Docker Run

If Docker is installed:

```bash
docker build -t ai-skill-backend ./backend
docker run --rm -p 8000:8000 --env-file ./backend/.env ai-skill-backend
```

---

## 14. Recommended Simple Local Setup For You

Since this is your first time with Supabase, the easiest path right now is:

1. start backend locally first without worrying about DB persistence
2. confirm health check and APIs work
3. add Gemini key
4. test end-to-end in Postman
5. create Supabase project after that
6. keep Supabase credentials ready for the next persistence integration step

This avoids getting blocked on DB setup before the actual hackathon demo flow is working.

---

## 15. Quick Manual Setup Checklist

- install Python
- create `.venv`
- activate `.venv`
- install requirements
- create `.env`
- fill CORS values
- add Gemini key if available
- optionally create Supabase project
- optionally copy Supabase DB credentials into `.env`
- run backend
- open `/docs`
- test using Postman

## Related Files

- backend env example:
  [backend/.env.example](C:\Users\janha\Desktop\deccan_ai\backend\.env.example)
- backend readme:
  [backend/README.md](C:\Users\janha\Desktop\deccan_ai\backend\README.md)
- backend testing guide:
  [BACKEND_TESTING_GUIDE.md](C:\Users\janha\Desktop\deccan_ai\BACKEND_TESTING_GUIDE.md)
