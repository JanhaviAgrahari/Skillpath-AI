from datetime import datetime
from threading import Lock
from uuid import UUID

from app.schemas.analysis import AnalysisResponse
from app.schemas.assessment import AssessmentRunState
from app.schemas.learning_plan import LearningPlan
from app.schemas.setup import ParsedJobDescriptionData, ParsedResumeData, SessionCreateRequest
from app.schemas.summary import FinalSummaryPayload


class InMemorySessionStore:
    """Simple session-scoped store for hackathon development and tests."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._sessions: dict[str, dict] = {}
        self._resume_documents: dict[str, dict] = {}
        self._job_descriptions: dict[str, dict] = {}
        self._analysis_results: dict[str, AnalysisResponse] = {}
        self._assessment_runs: dict[str, AssessmentRunState] = {}
        self._learning_plans: dict[str, LearningPlan] = {}
        self._summaries: dict[str, FinalSummaryPayload] = {}
        self._conversation_histories: dict[str, list[dict]] = {}

    def create_session(self, session_id: UUID, payload: SessionCreateRequest) -> dict:
        record = {
            "session_id": session_id,
            "user_name": payload.user_name,
            "target_role": payload.target_role,
            "experience_level": payload.experience_level,
            "status": "created",
            "current_step": "setup",
            "created_at": datetime.utcnow(),
        }
        with self._lock:
            self._sessions[str(session_id)] = record
        return record

    def get_session(self, session_id: UUID) -> dict | None:
        return self._sessions.get(str(session_id))

    def set_resume(self, session_id: UUID, payload: dict, parsed_data: ParsedResumeData) -> None:
        with self._lock:
            self._resume_documents[str(session_id)] = {
                "metadata": payload,
                "parsed_data": parsed_data,
            }
            session = self._sessions.get(str(session_id))
            if session:
                session["status"] = "documents_uploaded"
                session["current_step"] = "analysis"

    def get_resume(self, session_id: UUID) -> dict | None:
        return self._resume_documents.get(str(session_id))

    def set_job_description(self, session_id: UUID, payload: dict, parsed_data: ParsedJobDescriptionData) -> None:
        with self._lock:
            self._job_descriptions[str(session_id)] = {
                "metadata": payload,
                "parsed_data": parsed_data,
            }
            session = self._sessions.get(str(session_id))
            if session:
                session["status"] = "documents_uploaded"
                session["current_step"] = "analysis"

    def get_job_description(self, session_id: UUID) -> dict | None:
        return self._job_descriptions.get(str(session_id))

    def set_analysis(self, session_id: UUID, payload: AnalysisResponse) -> None:
        with self._lock:
            self._analysis_results[str(session_id)] = payload
            session = self._sessions.get(str(session_id))
            if session:
                session["status"] = "analysis_completed"
                session["current_step"] = "assessment"

    def get_analysis(self, session_id: UUID) -> AnalysisResponse | None:
        return self._analysis_results.get(str(session_id))

    def set_assessment_run(self, session_id: UUID, payload: AssessmentRunState) -> None:
        with self._lock:
            self._assessment_runs[str(session_id)] = payload
            session = self._sessions.get(str(session_id))
            if session:
                session["status"] = "assessment_in_progress"
                session["current_step"] = "assessment"

    def get_assessment_run(self, session_id: UUID) -> AssessmentRunState | None:
        return self._assessment_runs.get(str(session_id))

    def complete_assessment_run(self, session_id: UUID, payload: AssessmentRunState) -> None:
        with self._lock:
            self._assessment_runs[str(session_id)] = payload
            session = self._sessions.get(str(session_id))
            if session:
                session["status"] = "assessment_completed"
                session["current_step"] = "learning_plan"

    def set_learning_plan(self, session_id: UUID, payload: LearningPlan) -> None:
        with self._lock:
            self._learning_plans[str(session_id)] = payload
            session = self._sessions.get(str(session_id))
            if session:
                session["status"] = "learning_plan_generated"
                session["current_step"] = "summary"

    def get_learning_plan(self, session_id: UUID) -> LearningPlan | None:
        return self._learning_plans.get(str(session_id))

    def set_summary(self, session_id: UUID, payload: FinalSummaryPayload) -> None:
        with self._lock:
            self._summaries[str(session_id)] = payload
            session = self._sessions.get(str(session_id))
            if session:
                session["status"] = "summary_generated"
                session["current_step"] = "summary"

    def get_summary(self, session_id: UUID) -> FinalSummaryPayload | None:
        return self._summaries.get(str(session_id))

    def set_conversation_history(self, session_id: UUID, history: list[dict]) -> None:
        with self._lock:
            self._conversation_histories[str(session_id)] = history

    def get_conversation_history(self, session_id: UUID) -> list[dict]:
        return self._conversation_histories.get(str(session_id), [])

    def append_conversation_turn(self, session_id: UUID, role: str, text: str) -> None:
        with self._lock:
            history = self._conversation_histories.setdefault(str(session_id), [])
            history.append({"role": role, "text": text})

    def reset(self) -> None:
        with self._lock:
            self._sessions.clear()
            self._resume_documents.clear()
            self._job_descriptions.clear()
            self._analysis_results.clear()
            self._assessment_runs.clear()
            self._learning_plans.clear()
            self._summaries.clear()
            self._conversation_histories.clear()


session_store = InMemorySessionStore()
