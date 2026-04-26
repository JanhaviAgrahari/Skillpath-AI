# Backend Testing Guide

This guide explains how to test the backend step by step in the correct order.

The backend supports both:
- individual endpoint testing
- one orchestration endpoint for session-based progression

If you are testing for the first time, use the order below.

## Before You Start

1. Start the backend locally.
2. Open Postman.
3. Create a new collection named `AI Skill Assessment Backend`.
4. Create an environment variable in Postman:
   - `base_url` = `http://localhost:8000`
5. For any endpoint that needs a `session_id`, save the session ID from the earlier response and reuse it.

## Recommended Test Order

1. Health check
2. Create session
3. Upload resume
4. Submit job description
5. Run analysis
6. Review complete analysis
7. Start assessment
8. Submit one or more answers
9. Complete assessment
10. Generate learning plan
11. Generate summary
12. Export summary
13. Optional: test the orchestration endpoint

---

## 1. Health Check

### Endpoint
`GET /health`

### What it does
Checks whether the backend process is running.

### What it is for
Use this first so you know the server is alive before testing the real workflow.

### Postman steps
- Click `New` -> `HTTP Request`
- Set method to `GET`
- URL: `{{base_url}}/health`
- Click `Send`

### What to expect
You should get:

```json
{
  "status": "ok"
}
```

---

## 2. Create Session

### Endpoint
`POST /api/v1/sessions`

### What it does
Creates a new session for one candidate workflow.

### What it is for
Everything in this backend is session-based. You need a session before uploading resume, JD, analysis, assessment, learning plan, or summary.

### Postman steps
- Use the `Body` tab
- Select `raw`
- Select `JSON`
- Paste:

```json
{
  "user_name": "Jane",
  "target_role": "Backend Engineer",
  "experience_level": "mid"
}
```

- Click `Send`

### Save this value
Copy the returned `session_id`.

In Postman, save it as an environment variable:
- Open the environment
- Add `session_id`
- Paste the value

---

## 3. Upload Resume

### Endpoint
`POST /api/v1/sessions/{session_id}/resume`

### What it does
Accepts either:
- a resume file
- resume text pasted manually

Then it parses and normalizes the resume for downstream analysis.

### What it is for
This creates the backend's structured resume snapshot.

### Option A: Test with pasted resume text

### Postman steps
- Use method `POST`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/resume`
- Open the `Body` tab
- Select `form-data`
- Add a key:
  - Key = `resume_text`
  - Type = `Text`
  - Value = your full resume text
- Click `Send`

### Option B: Test with a file

### Postman steps
- Open `Body`
- Select `form-data`
- Add a key:
  - Key = `resume_file`
  - Type = `File`
  - Value = choose a `.txt`, `.pdf`, or `.docx` file
- Click `Send`

### Postman interface notes
- Use `Body` -> `form-data`
- For file upload, the key type must be changed from `Text` to `File`

### What to expect
You should get parsed resume data like:
- name
- email
- phone
- skills
- experience
- normalized text

---

## 4. Submit Job Description

### Endpoint
`POST /api/v1/sessions/{session_id}/job-description`

### What it does
Accepts a pasted job description and parses it into structured JD fields.

### What it is for
This creates the structured JD snapshot that is later compared with the resume.

### Postman steps
- Method: `POST`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/job-description`
- Open `Body`
- Select `raw`
- Select `JSON`
- Paste:

```json
{
  "title": "Backend Engineer",
  "company_name": "Acme",
  "raw_text": "Backend Engineer role focused on backend systems and platform APIs. Required Skills: Python, FastAPI, Docker, PostgreSQL, REST APIs. Preferred: CI/CD, Kubernetes. Responsibilities: Build APIs, improve backend reliability, and own service performance. Qualifications: 3+ years backend engineering experience."
}
```

- Click `Send`

### Postman interface notes
- Use `Body` -> `raw` -> `JSON`

---

## 5. Run Skill Analysis

### Endpoint
`POST /api/v1/sessions/{session_id}/analysis/run`

### What it does
Runs:
- skill extraction
- skill normalization
- resume vs JD comparison
- gap analysis

### What it is for
This powers the Skill Analysis screen in the frontend.

### Postman steps
- Method: `POST`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/analysis/run`
- `Body` -> `raw` -> `JSON`
- Paste:

```json
{
  "normalize_skills": true,
  "include_adjacent_skills": true
}
```

- Click `Send`

### What to expect
You should see:
- strong matches
- partial matches
- missing skills
- adjacent skills
- role match score
- explanation summary

---

## 6. Get Complete Analysis

### Endpoint
`GET /api/v1/sessions/{session_id}/analysis/complete`

### What it does
Returns the full analysis package in one response:
- parsed resume snapshot
- parsed JD snapshot
- analysis result

### What it is for
Use this when you want one complete payload for the Skill Analysis screen.

### Postman steps
- Method: `GET`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/analysis/complete`
- Click `Send`

---

## 7. Start Assessment

### Endpoint
`POST /api/v1/sessions/{session_id}/assessment/start`

### What it does
Creates an assessment run and generates targeted questions for selected skills.

### What it is for
This powers the Assessment Workspace chat flow.

### Postman steps
- Method: `POST`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/assessment/start`
- `Body` -> `raw` -> `JSON`
- Paste:

```json
{
  "skills_to_assess": ["Docker", "PostgreSQL"],
  "questions_per_skill": 1,
  "expected_level": "intermediate"
}
```

- Click `Send`

### Save this value
Copy `current_question.question_id`

Save it as `question_id` in Postman environment if you want.

---

## 8. Submit Assessment Answer

### Endpoint
`POST /api/v1/sessions/{session_id}/assessment/answer`

### What it does
Evaluates one answer, updates the skill score, and may return a follow-up or next question.

### What it is for
This is the core conversational assessment behavior.

### Postman steps
- Method: `POST`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/assessment/answer`
- `Body` -> `raw` -> `JSON`
- Paste:

```json
{
  "question_id": "{{question_id}}",
  "answer_text": "I would start with a Dockerfile, use environment variables, build a lean image, and then use Docker Compose to run the FastAPI app and database together locally."
}
```

- Click `Send`

### What to expect
You should get:
- evaluation result
- updated score
- updated proficiency
- `next_question` if the flow continues

### Repeat if needed
If a `next_question` is returned:
1. copy its `question_id`
2. submit another answer

---

## 9. Complete Assessment

### Endpoint
`POST /api/v1/sessions/{session_id}/assessment/complete`

### What it does
Finalizes the assessment and returns summarized per-skill scores.

### What it is for
Use this after you are done answering assessment questions.

### Postman steps
- Method: `POST`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/assessment/complete`
- No body needed
- Click `Send`

---

## 10. Generate Learning Plan

### Endpoint
`POST /api/v1/sessions/{session_id}/learning-plan/generate`

### What it does
Builds a personalized learning roadmap from:
- gap analysis
- assessment scores
- preferred intensity

### What it is for
This powers the Learning Plan screen.

### Postman steps
- Method: `POST`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/learning-plan/generate`
- `Body` -> `raw` -> `JSON`
- Paste:

```json
{
  "weeks": 4,
  "hours_per_week": 5,
  "focus_skills": ["Docker", "PostgreSQL"],
  "preferred_learning_style": "project_based",
  "intensity": "standard"
}
```

- Click `Send`

### What to expect
You should get:
- roadmap overview
- prioritized skills
- weekly milestones
- tasks
- resources
- time estimates

---

## 11. Get Learning Plan

### Endpoint
`GET /api/v1/sessions/{session_id}/learning-plan`

### What it does
Fetches the stored learning plan.

### What it is for
Use this when the frontend needs to re-open the Learning Plan screen without regenerating.

### Postman steps
- Method: `GET`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/learning-plan`
- Click `Send`

---

## 12. Generate Final Summary

### Endpoint
`POST /api/v1/sessions/{session_id}/summary/generate`

### What it does
Builds the final report using:
- role fit
- skill analysis
- assessment
- learning plan

### What it is for
This powers the Summary / Export screen.

### Postman steps
- Method: `POST`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/summary/generate`
- No body needed
- Click `Send`

### What to expect
You should get:
- candidate summary
- role summary
- overall match score
- skill analysis summary
- assessment summary
- strongest areas
- biggest gaps
- recommended next steps
- learning plan summary

---

## 13. Get Final Summary

### Endpoint
`GET /api/v1/sessions/{session_id}/summary`

### What it does
Returns the stored final report payload.

### What it is for
Use this when the frontend wants the final summary without regenerating it.

### Postman steps
- Method: `GET`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/summary`
- Click `Send`

---

## 14. Export Payload

### Endpoint
`GET /api/v1/sessions/{session_id}/export`

### What it does
Returns a structured export-ready JSON report.

### What it is for
This is the payload you can later transform into PDF or downloadable report output.

### Postman steps
- Method: `GET`
- URL:
  `{{base_url}}/api/v1/sessions/{{session_id}}/export`
- Click `Send`

---

## 15. Optional: Test the Orchestration Endpoint

### Endpoint
`POST /api/v1/workflow/orchestrate`

### What it does
Allows the frontend to drive the workflow step by step from one endpoint.

### What it is for
Use this if you want one session-aware endpoint that progresses through the workflow instead of calling every route separately.

### Important
This endpoint uses `form-data`.

### Postman steps
- Method: `POST`
- URL:
  `{{base_url}}/api/v1/workflow/orchestrate`
- Open `Body`
- Select `form-data`

### Example intake request fields
- `workflow_step` = `intake`
- `user_name` = `Jane`
- `target_role` = `Backend Engineer`
- `experience_level` = `mid`
- `resume_text` = full resume text
- `job_description_text` = full JD text
- `job_title` = `Backend Engineer`
- `company_name` = `Acme`

### Postman interface notes
- Use `Body` -> `form-data`
- For arrays like `skills_to_assess_json`, pass a JSON string like:

```json
["Docker", "PostgreSQL"]
```

---

## Suggested Full Demo Path in Postman

If you want the cleanest hackathon demo flow, use this order:

1. `GET /health`
2. `POST /api/v1/sessions`
3. `POST /api/v1/sessions/{session_id}/resume`
4. `POST /api/v1/sessions/{session_id}/job-description`
5. `POST /api/v1/sessions/{session_id}/analysis/run`
6. `GET /api/v1/sessions/{session_id}/analysis/complete`
7. `POST /api/v1/sessions/{session_id}/assessment/start`
8. `POST /api/v1/sessions/{session_id}/assessment/answer`
9. repeat answer calls if needed
10. `POST /api/v1/sessions/{session_id}/assessment/complete`
11. `POST /api/v1/sessions/{session_id}/learning-plan/generate`
12. `POST /api/v1/sessions/{session_id}/summary/generate`
13. `GET /api/v1/sessions/{session_id}/export`

## Useful Postman Tabs to Use

- `Params`:
  not needed for most current endpoints
- `Authorization`:
  not needed right now because there is no auth in the hackathon MVP
- `Headers`:
  usually Postman sets `Content-Type` automatically
- `Body -> raw -> JSON`:
  use for most JSON APIs
- `Body -> form-data`:
  use for file upload and the orchestration endpoint
- `Tests`:
  optional, you can store `session_id` and `question_id` automatically if you want

## Common Mistakes

- forgetting to create a session first
- using the wrong `session_id`
- sending resume upload as `raw JSON` instead of `form-data`
- starting assessment before running analysis
- generating summary before the earlier steps have data
- forgetting to update `question_id` when submitting the next answer

## Where Sample Payloads Are Stored

Inside the backend folder:
- `backend/sample_data/payloads/`
- `backend/sample_data/api/requests/`
- `backend/sample_data/api/responses/`
- `backend/sample_data/files/`
