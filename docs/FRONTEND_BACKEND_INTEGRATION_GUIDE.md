# Frontend Backend Integration Guide

This document is the main handoff guide for connecting the frontend and backend of the project:

`AI-Powered Skill Assessment & Personalised Learning Plan Agent`

It is written for:
- frontend developers
- backend developers
- AI coding tools
- integration partners

The goal is to make integration easy, consistent, and safe.

---

# 1. Project Integration Overview

The product flow has 5 frontend screens:

1. Landing / Setup
2. Assessment Workspace
3. Skill Analysis
4. Learning Plan
5. Summary / Export

The backend is session-based.

That means:
- every user flow starts by creating one backend session
- all later API calls must use the same `session_id`
- the frontend should store the active `session_id` in app state

Important:
- without the correct `session_id`, the backend cannot continue the workflow
- all page transitions in the frontend should be tied to backend session state

---

# 2. Backend Base Information

## Base URL

Local default:

```text
http://localhost:8000
```

Main API prefix:

```text
/api/v1
```

So most APIs look like:

```text
http://localhost:8000/api/v1/...
```

## Response Pattern

Most successful APIs return:

```json
{
  "success": true,
  "message": {
    "code": "ok",
    "message": "success"
  },
  "data": {},
  "timestamp": "..."
}
```

Most error APIs return:

```json
{
  "success": false,
  "error_code": "some_error_code",
  "error_message": "Readable error message",
  "details": {},
  "timestamp": "..."
}
```

Frontend rule:
- always check `success`
- if `success` is false, display `error_message`
- optionally use `details` for debugging or inline validation messaging

---

# 3. Main Backend Concepts Frontend Must Know

## 3.1 `session_id`

This is the core identifier for one candidate workflow.

Frontend must:
- create it once at setup
- keep it in memory
- persist it if needed in local storage or route state
- pass it into every later API path

## 3.2 Session State

Backend tracks session progression using:
- `status`
- `current_step`

Possible session states include:
- `created`
- `documents_uploaded`
- `analysis_completed`
- `assessment_in_progress`
- `assessment_completed`
- `learning_plan_generated`
- `summary_generated`

Possible steps include:
- `setup`
- `analysis`
- `assessment`
- `learning_plan`
- `summary`

Frontend should use this to:
- guard page navigation
- recover page state on refresh
- know what data should already exist

## 3.3 Independent Endpoints vs Orchestration Endpoint

There are two integration styles:

### Option A: Independent endpoint flow
Use dedicated APIs page by page.

This is best if:
- frontend already has clear page logic
- you want more control
- you want easier debugging

### Option B: Orchestration endpoint
Use:

```text
POST /api/v1/workflow/orchestrate
```

This is best if:
- you want one backend-controlled step flow
- you want simpler step progression logic

Recommendation:
- use dedicated endpoints for most page-specific UI
- use orchestration endpoint only if you want a central wizard-like controller

---

# 4. Screen-by-Screen Integration

---

## Screen 1: Landing / Setup

This screen usually does:
- collect candidate name or user name
- collect target role
- collect experience level
- accept resume upload or resume text
- accept job description text
- create session

### Backend APIs Needed

1. `POST /api/v1/sessions`
2. `POST /api/v1/sessions/{session_id}/resume`
3. `POST /api/v1/sessions/{session_id}/job-description`
4. Optional: `GET /api/v1/sessions/{session_id}`

### Recommended UI Flow

1. user enters setup info
2. frontend calls `POST /sessions`
3. save `session_id`
4. upload resume
5. submit JD
6. when both succeed, allow move to analysis screen

### Request Details

#### Create Session

```json
{
  "user_name": "Jane",
  "target_role": "Backend Engineer",
  "experience_level": "mid"
}
```

#### Resume Upload

Use `form-data`

Either:
- `resume_file`

or:
- `resume_text`

Important:
- do not send both at the same time

#### Job Description Submit

```json
{
  "title": "Backend Engineer",
  "company_name": "Acme",
  "raw_text": "Full job description..."
}
```

### What Frontend Should Store

Store:
- `session_id`
- parsed resume response
- parsed JD response

These can help:
- prefill later summary
- show confirmation cards on setup screen

### Important UI Notes

- resume upload must use `form-data`
- JD submit uses `raw JSON`
- show clear status:
  - session created
  - resume parsed
  - JD parsed
- if parsing fails, show backend message directly

### Common Integration Mistakes

- forgetting to save `session_id`
- sending resume as raw JSON instead of `form-data`
- allowing user to continue before both resume and JD are uploaded

---

## Screen 2: Assessment Workspace

This screen usually does:
- show selected skills to assess
- show current interview-style question
- accept typed user answer
- display evaluation result
- move to next question

### Backend APIs Needed

1. `POST /api/v1/sessions/{session_id}/assessment/start`
2. `GET /api/v1/sessions/{session_id}/assessment`
3. `POST /api/v1/sessions/{session_id}/assessment/answer`
4. `POST /api/v1/sessions/{session_id}/assessment/complete`

### Important Dependency

Assessment should only start after analysis is completed.

### Recommended UI Flow

1. frontend gets assessment recommendation skills from analysis response
2. user selects skills or uses suggested ones
3. call `assessment/start`
4. render `current_question`
5. user submits answer
6. call `assessment/answer`
7. render:
   - evaluation
   - updated score
   - next question
8. repeat until no more questions
9. call `assessment/complete`

### Assessment Start Request

```json
{
  "skills_to_assess": ["Docker", "PostgreSQL"],
  "questions_per_skill": 1,
  "expected_level": "intermediate"
}
```

### Assessment Answer Request

```json
{
  "question_id": "uuid-here",
  "answer_text": "My answer..."
}
```

### What Frontend Should Read From Response

From `assessment/start`:
- `assessment_id`
- `current_question`
- `questions`
- `progress`

From `assessment/answer`:
- `evaluation`
- `skill_score`
- `skill_proficiency`
- `next_question`
- `progress`

From `assessment/complete`:
- `skill_scores`
- `overall_assessment_summary`

### UI Recommendations

- design this like a chat, not like a multiple-choice quiz
- current question should look like interviewer prompt
- answer box should remain simple text input
- show evaluation in a side panel or below the answer
- show progress like:
  - `1 of 4 questions answered`

### Important Integration Notes

- always use the latest `question_id`
- if `next_question` is null, assessment may be complete
- do not assume one skill means one question only
- follow-up questions may happen automatically

### Common Mistakes

- sending an answer with an old `question_id`
- starting assessment before analysis
- assuming skill score is final before completion

---

## Screen 3: Skill Analysis

This screen usually does:
- show extracted resume skills
- show extracted JD skills
- show strong, partial, missing, adjacent groups
- show role match score
- show explanation summary

### Backend APIs Needed

1. `POST /api/v1/sessions/{session_id}/analysis/run`
2. `GET /api/v1/sessions/{session_id}/analysis`
3. `GET /api/v1/sessions/{session_id}/analysis/complete`

### Recommended UI Flow

1. after resume and JD upload, call `analysis/run`
2. use `analysis/complete` for page rendering
3. optionally cache analysis result in frontend state

### Why `analysis/complete` is Best For This Screen

Because it returns:
- parsed resume snapshot
- parsed JD snapshot
- complete skill analysis in one payload

That is usually enough to power the full page.

### What Frontend Should Render

#### Resume Skills
Show:
- name
- category
- confidence

#### JD Skills
Show:
- name
- category

#### Strong Matches
Show:
- skill
- reason
- score

#### Partial Matches
Show:
- skill
- mapped skill
- reason

#### Missing Skills
Show:
- skill
- reason

#### Adjacent Skills
Show:
- skill
- reason

#### Role Fit
Show:
- `role_match_score`
- `role_match_label`
- `explanation_summary`

### Important UI Notes

- role score is from 0 to 100
- do not treat confidence and score as the same thing
- `reason` fields are intentionally explainable, show them in UI

### Common Mistakes

- only displaying skill names without reasons
- ignoring `partial_matches`
- not showing role summary near the top

---

## Screen 4: Learning Plan

This screen usually does:
- show prioritized roadmap
- show weekly plan
- show tasks and resources
- show total time estimate
- support different intensity modes

### Backend APIs Needed

1. `POST /api/v1/sessions/{session_id}/learning-plan/generate`
2. `GET /api/v1/sessions/{session_id}/learning-plan`

### Recommended UI Flow

1. analysis should exist first
2. assessment should ideally be completed first for better personalization
3. user chooses:
   - weeks
   - hours per week
   - intensity
   - optional focus skills
4. call generate
5. render plan

### Learning Plan Request

```json
{
  "weeks": 4,
  "hours_per_week": 5,
  "focus_skills": ["Docker", "PostgreSQL"],
  "preferred_learning_style": "project_based",
  "intensity": "standard"
}
```

### What Frontend Should Render

From `overview`:
- goal
- estimated total hours
- intensity
- prioritized skills
- rationale

From each milestone:
- week
- title
- focus
- topics
- tasks
- outcomes
- resources
- estimated hours

From each resource:
- title
- resource type
- provider
- url
- notes

### UI Recommendations

- make milestones collapsible by week
- make resource links clickable
- show intensity clearly:
  - gentle
  - standard
  - intensive
- show total hours and total weeks near the top

### Common Mistakes

- not exposing tasks separately from topics
- hiding resource URLs
- not letting user choose intensity

---

## Screen 5: Summary / Export

This screen usually does:
- show final candidate summary
- show role fit summary
- show strongest areas
- show biggest gaps
- show assessment summary
- show plan summary
- allow export later

### Backend APIs Needed

1. `POST /api/v1/sessions/{session_id}/summary/generate`
2. `GET /api/v1/sessions/{session_id}/summary`
3. `GET /api/v1/sessions/{session_id}/export`

### Recommended UI Flow

1. after learning plan is generated, call `summary/generate`
2. render summary page
3. use `export` payload for future PDF/download feature

### What Frontend Should Render

#### Candidate Profile
- candidate name
- target role
- current fit
- experience level

#### Role Summary
- overall match score
- fit label
- explanation

#### Highlights
- strongest skills
- main gaps

#### Skill Analysis Summary
- strong matches
- partial matches
- missing skills
- adjacent skills
- explanation

#### Assessment Summary
- overall average score
- per-skill scores
- explanation

#### Learning Plan Summary
- total weeks
- total hours
- top milestones
- explanation

#### Recommended Next Steps
- render as short action list

### Export

Use:

```text
GET /api/v1/sessions/{session_id}/export
```

This returns:
- final report
- export metadata

### Important UI Notes

- export payload is JSON for now
- do not wait for PDF generation now unless you add it later
- keep this page readable and structured because judges may spend time here

---

# 5. Best Integration Strategy For Frontend

For the current codebase, the safest frontend integration strategy is:

1. use dedicated endpoints page by page
2. store `session_id` globally
3. store last successful response for each stage
4. use `GET` endpoints on refresh or revisit

Recommended frontend state shape:

```ts
{
  sessionId: string | null,
  session: {},
  resume: {},
  jobDescription: {},
  analysis: {},
  assessment: {},
  learningPlan: {},
  summary: {}
}
```

Best place to keep it:
- React context
- Zustand
- Redux
- route-based state + local storage

---

# 6. When To Use Orchestration Endpoint

Use:

```text
POST /api/v1/workflow/orchestrate
```

if you want:
- one backend-guided step system
- a wizard-like integration
- a central state response after each action

It is especially useful for:
- AI tool driven integration
- internal admin/demo flows
- frontend prototypes

But for a polished product UI, dedicated endpoints may still be cleaner.

### Workflow Step Values

- `intake`
- `analysis`
- `assessment_start`
- `assessment_answer`
- `assessment_complete`
- `learning_plan`
- `summary`
- `state`

### Orchestration Important Note

This endpoint uses `form-data`, not plain JSON.

That matters because:
- resume file upload is supported there
- array fields like skills are passed as JSON strings

Example:
- `skills_to_assess_json = ["Docker","PostgreSQL"]`

---

# 7. Integration Rules To Give AI Tools

If another AI tool helps integrate frontend and backend, give it these rules:

1. Always create and persist `session_id` before calling step-specific APIs.
2. Never call assessment endpoints before analysis exists.
3. Never call summary/export before learning plan or at least analysis is available.
4. Use `form-data` only where required:
   - resume upload
   - orchestration endpoint
5. Use raw JSON for all standard JSON endpoints.
6. Show backend `error_message` directly in the UI.
7. Treat `next_question` as the single source of truth for the next assessment step.
8. For revisits or reloads, prefer calling `GET` endpoints instead of regenerating everything.
9. Render explanation fields from backend, do not hide them.
10. Do not fabricate frontend-derived skill scoring when backend already returns it.

---

# 8. Integration Rules To Give Developers

1. Keep backend contracts unchanged unless both frontend and backend are updated together.
2. Reuse schema field names exactly as returned by backend.
3. Do not rename fields in the frontend adapter unless absolutely necessary.
4. If creating frontend types, derive them directly from backend response shapes.
5. Keep page transitions aligned with backend progression:
   - setup -> analysis -> assessment -> learning plan -> summary
6. If adding caching, cache by `session_id`.
7. If allowing browser refresh recovery, fetch:
   - session
   - analysis
   - assessment
   - learning plan
   - summary
8. If integrating file upload, always use `multipart/form-data`.
9. If integrating export later, use the backend export JSON as the source of truth for PDF composition.

---

# 9. Suggested Frontend Button Wiring

This section maps common frontend buttons to backend calls.

## Landing / Setup Page

Button: `Start Assessment Journey`
- call `POST /sessions`

Button: `Upload Resume`
- call `POST /sessions/{session_id}/resume`

Button: `Submit Job Description`
- call `POST /sessions/{session_id}/job-description`

Button: `Continue To Analysis`
- call `POST /sessions/{session_id}/analysis/run`

## Skill Analysis Page

Button: `Generate Analysis`
- call `POST /analysis/run`

Button: `Refresh Analysis`
- call `GET /analysis/complete`

Button: `Start Skill Assessment`
- navigate to assessment page with recommended skills

## Assessment Workspace

Button: `Start Interview`
- call `POST /assessment/start`

Button: `Send Answer`
- call `POST /assessment/answer`

Button: `Finish Assessment`
- call `POST /assessment/complete`

## Learning Plan Page

Button: `Generate Plan`
- call `POST /learning-plan/generate`

Button: `Reload Plan`
- call `GET /learning-plan`

## Summary / Export Page

Button: `Generate Final Summary`
- call `POST /summary/generate`

Button: `Refresh Summary`
- call `GET /summary`

Button: `Export Report`
- call `GET /export`

---

# 10. Error Handling Guidance For Frontend

Always assume an API may fail.

Show friendly messages for:
- missing `session_id`
- invalid file type
- bad request payload
- trying to run a step out of order
- LLM fallback or timeout cases

Suggested frontend error pattern:

1. check `success`
2. if false:
   - show `error_message`
   - optionally log `details`
3. keep user on current page
4. allow retry

### Common Error Cases

#### Resume error
Show:
- unsupported file type
- empty file
- bad parsing

#### Assessment error
Show:
- invalid current question
- stale question ID
- assessment not started

#### Summary error
Show:
- analysis missing
- summary not ready

---

# 11. Current Backend Limitations Frontend Should Know

These are important.

## In-memory session store

Current active session state is stored in memory.

That means:
- if backend restarts, session data resets
- frontend should expect this during local development

## Supabase runtime persistence not fully wired yet

The backend includes:
- Supabase-ready config
- SQLAlchemy models
- async DB session setup

But active workflow services still use in-memory runtime state for now.

Frontend implication:
- current integration works fully for demo flow
- but data persistence across restarts is not guaranteed yet

## PDF export not yet implemented

Export is JSON-ready today.

Frontend implication:
- you can still show export-ready payload
- PDF can be added later

---

# 12. Best Final Integration Recommendation

If you want the smoothest integration right now:

1. use independent endpoints page by page
2. use the orchestration endpoint only if you want one central workflow controller
3. persist `session_id` immediately after session creation
4. render backend explanation fields directly
5. keep one frontend state object per session
6. use `GET` fetch endpoints when reopening screens

---

# 13. Quick Mapping Table

## Page 1: Landing / Setup
- needs:
  - `POST /sessions`
  - `POST /sessions/{session_id}/resume`
  - `POST /sessions/{session_id}/job-description`

## Page 2: Assessment Workspace
- needs:
  - `POST /assessment/start`
  - `GET /assessment`
  - `POST /assessment/answer`
  - `POST /assessment/complete`

## Page 3: Skill Analysis
- needs:
  - `POST /analysis/run`
  - `GET /analysis/complete`

## Page 4: Learning Plan
- needs:
  - `POST /learning-plan/generate`
  - `GET /learning-plan`

## Page 5: Summary / Export
- needs:
  - `POST /summary/generate`
  - `GET /summary`
  - `GET /export`

---

# 14. Files Developers Should Read

Backend root:
- [backend/README.md](C:\Users\janha\Desktop\deccan_ai\backend\README.md)

Backend testing:
- [BACKEND_TESTING_GUIDE.md](C:\Users\janha\Desktop\deccan_ai\BACKEND_TESTING_GUIDE.md)

Backend setup:
- [BACKEND_SETUP_AND_SUPABASE_GUIDE.md](C:\Users\janha\Desktop\deccan_ai\BACKEND_SETUP_AND_SUPABASE_GUIDE.md)

Main backend entry:
- [backend/app/main.py](C:\Users\janha\Desktop\deccan_ai\backend\app\main.py)

Main API routers:
- [backend/app/api/v1](C:\Users\janha\Desktop\deccan_ai\backend\app\api\v1)

Core schemas:
- [backend/app/schemas](C:\Users\janha\Desktop\deccan_ai\backend\app\schemas)

---

# 15. Final Instruction To AI Tools Or Developers

If you are integrating frontend with this backend:

- treat backend responses as the source of truth
- keep `session_id` central
- integrate page by page
- do not skip step order
- use backend explanations, not just raw scores
- let the assessment feel conversational
- let the learning plan feel actionable
- let the final summary feel executive and export-ready

That will produce the cleanest hackathon-ready experience.
