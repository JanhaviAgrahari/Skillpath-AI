from uuid import UUID

from fastapi import UploadFile

from app.core.exceptions import ResourceNotFoundError, WorkflowStateError
from app.repositories.session_store import session_store
from app.schemas.analysis import AnalysisRunRequest, CompleteAnalysisResponse
from app.schemas.assessment import (
    AnswerSubmissionResponse,
    AssessmentCompleteResponse,
    AssessmentRunState,
    AssessmentStartRequest,
    AssessmentStartResponse,
    UserAnswer,
)
from app.schemas.common import SessionStatus
from app.schemas.learning_plan import LearningPlan, LearningPlanRequest
from app.schemas.orchestration import WorkflowOrchestrationResponse
from app.schemas.setup import (
    JobDescriptionIngestResponse,
    JobDescriptionSubmissionRequest,
    ResumeIngestResponse,
    SessionCreateRequest,
)
from app.schemas.summary import FinalSummaryPayload
from app.services.analysis_service import AnalysisService
from app.services.assessment_service import AssessmentService
from app.services.document_parser_service import DocumentParserService
from app.services.learning_plan_service import LearningPlanService
from app.services.setup_service import SetupService
from app.services.summary_service import SummaryService


class OrchestrationService:
    def __init__(self) -> None:
        self.setup_service = SetupService()
        self.document_parser_service = DocumentParserService()
        self.analysis_service = AnalysisService()
        self.assessment_service = AssessmentService()
        self.learning_plan_service = LearningPlanService()
        self.summary_service = SummaryService()

    async def advance(
        self,
        workflow_step: str,
        session_id: UUID | None = None,
        user_name: str | None = None,
        target_role: str | None = None,
        experience_level: str | None = None,
        resume_text: str | None = None,
        resume_file: UploadFile | None = None,
        job_description_text: str | None = None,
        job_title: str | None = None,
        company_name: str | None = None,
        skills_to_assess: list[str] | None = None,
        questions_per_skill: int = 2,
        expected_level: str = "intermediate",
        question_id: UUID | None = None,
        answer_text: str | None = None,
        plan_weeks: int = 6,
        plan_hours_per_week: int = 6,
        plan_intensity: str = "standard",
        plan_focus_skills: list[str] | None = None,
        preferred_learning_style: str | None = None,
    ) -> WorkflowOrchestrationResponse:
        if workflow_step == "intake":
            return await self._handle_intake(
                session_id=session_id,
                user_name=user_name,
                target_role=target_role,
                experience_level=experience_level,
                resume_text=resume_text,
                resume_file=resume_file,
                job_description_text=job_description_text,
                job_title=job_title,
                company_name=company_name,
            )
        if session_id is None:
            raise WorkflowStateError("session_id is required for this workflow step.")
        if workflow_step == "analysis":
            await self.analysis_service.run_analysis(session_id, AnalysisRunRequest())
            analysis = await self.analysis_service.get_complete_analysis(session_id)
            return await self._build_state_response(
                session_id=session_id,
                workflow_step=workflow_step,
                analysis=analysis,
            )
        if workflow_step == "assessment_start":
            assessment_start = await self.assessment_service.start_assessment(
                session_id,
                AssessmentStartRequest(
                    skills_to_assess=skills_to_assess or [],
                    questions_per_skill=questions_per_skill,
                    expected_level=expected_level,
                ),
            )
            return await self._build_state_response(
                session_id=session_id,
                workflow_step=workflow_step,
                assessment_start=assessment_start,
            )
        if workflow_step == "assessment_answer":
            if question_id is None or not answer_text:
                raise WorkflowStateError("question_id and answer_text are required for assessment_answer.")
            assessment_answer = await self.assessment_service.submit_answer(
                session_id,
                UserAnswer(question_id=question_id, answer_text=answer_text),
            )
            return await self._build_state_response(
                session_id=session_id,
                workflow_step=workflow_step,
                assessment_answer=assessment_answer,
            )
        if workflow_step == "assessment_complete":
            assessment_complete = await self.assessment_service.complete_assessment(session_id)
            return await self._build_state_response(
                session_id=session_id,
                workflow_step=workflow_step,
                assessment_complete=assessment_complete,
            )
        if workflow_step == "learning_plan":
            learning_plan = await self.learning_plan_service.generate_plan(
                session_id,
                LearningPlanRequest(
                    weeks=plan_weeks,
                    hours_per_week=plan_hours_per_week,
                    focus_skills=plan_focus_skills or [],
                    preferred_learning_style=preferred_learning_style,
                    intensity=plan_intensity,
                ),
            )
            return await self._build_state_response(
                session_id=session_id,
                workflow_step=workflow_step,
                learning_plan=learning_plan,
            )
        if workflow_step == "summary":
            summary = await self.summary_service.generate_summary(session_id)
            return await self._build_state_response(
                session_id=session_id,
                workflow_step=workflow_step,
                summary=summary,
            )
        if workflow_step == "state":
            return await self._build_state_response(session_id=session_id, workflow_step=workflow_step)
        raise WorkflowStateError(f"Unsupported workflow_step '{workflow_step}'.")

    async def _handle_intake(
        self,
        session_id: UUID | None,
        user_name: str | None,
        target_role: str | None,
        experience_level: str | None,
        resume_text: str | None,
        resume_file: UploadFile | None,
        job_description_text: str | None,
        job_title: str | None,
        company_name: str | None,
    ) -> WorkflowOrchestrationResponse:
        if session_id is None:
            if not target_role:
                raise WorkflowStateError("target_role is required when creating a new session.")
            session_payload = await self.setup_service.create_session(
                SessionCreateRequest(
                    user_name=user_name,
                    target_role=target_role,
                    experience_level=experience_level,
                )
            )
            session_id = session_payload.session_id
        else:
            if session_store.get_session(session_id) is None:
                raise ResourceNotFoundError(f"Session '{session_id}' was not found.")

        resume = None
        if resume_file is not None or resume_text:
            resume = await self.document_parser_service.ingest_resume(
                session_id=session_id,
                resume_file=resume_file,
                resume_text=resume_text,
            )
        job_description = None
        if job_description_text:
            job_description = await self.document_parser_service.ingest_job_description(
                session_id=session_id,
                payload=JobDescriptionSubmissionRequest(
                    title=job_title,
                    company_name=company_name,
                    raw_text=job_description_text,
                ),
            )
        return await self._build_state_response(
            session_id=session_id,
            workflow_step="intake",
            resume=resume,
            job_description=job_description,
        )

    async def _build_state_response(
        self,
        session_id: UUID,
        workflow_step: str,
        resume: ResumeIngestResponse | None = None,
        job_description: JobDescriptionIngestResponse | None = None,
        analysis: CompleteAnalysisResponse | None = None,
        assessment_start: AssessmentStartResponse | None = None,
        assessment_answer: AnswerSubmissionResponse | None = None,
        assessment_complete: AssessmentCompleteResponse | None = None,
        learning_plan: LearningPlan | None = None,
        summary: FinalSummaryPayload | None = None,
    ) -> WorkflowOrchestrationResponse:
        session = await self.setup_service.get_session(session_id)
        resume = resume or self._resume_response(session_id)
        job_description = job_description or self._jd_response(session_id)
        analysis = analysis or await self._safe_complete_analysis(session_id)
        assessment_state = self._safe_assessment_state(session_id)
        learning_plan = learning_plan or self._safe_learning_plan(session_id)
        summary = summary or self._safe_summary(session_id)

        return WorkflowOrchestrationResponse(
            session_id=session_id,
            workflow_step=workflow_step,
            session_status=session.status,
            current_step=session.current_step,
            available_actions=self._available_actions(session.status),
            session=session,
            resume=resume,
            job_description=job_description,
            analysis=analysis,
            assessment_start=assessment_start or self._assessment_start_response(assessment_state),
            assessment_state=assessment_state,
            assessment_answer=assessment_answer,
            assessment_complete=assessment_complete or self._assessment_complete_response(assessment_state),
            learning_plan=learning_plan,
            summary=summary,
        )

    def _resume_response(self, session_id: UUID) -> ResumeIngestResponse | None:
        entry = session_store.get_resume(session_id)
        if entry is None:
            return None
        metadata = entry["metadata"]
        return ResumeIngestResponse(
            session_id=session_id,
            document_id=metadata["document_id"],
            source_type=metadata["source_type"],
            filename=metadata["filename"],
            parsed_data=entry["parsed_data"],
            status=SessionStatus.DOCUMENTS_UPLOADED,
        )

    def _jd_response(self, session_id: UUID) -> JobDescriptionIngestResponse | None:
        entry = session_store.get_job_description(session_id)
        if entry is None:
            return None
        metadata = entry["metadata"]
        return JobDescriptionIngestResponse(
            session_id=session_id,
            document_id=metadata["document_id"],
            parsed_data=entry["parsed_data"],
            status=SessionStatus.DOCUMENTS_UPLOADED,
        )

    async def _safe_complete_analysis(self, session_id: UUID) -> CompleteAnalysisResponse | None:
        try:
            return await self.analysis_service.get_complete_analysis(session_id)
        except ResourceNotFoundError:
            return None

    def _safe_assessment_state(self, session_id: UUID) -> AssessmentRunState | None:
        return session_store.get_assessment_run(session_id)

    def _safe_learning_plan(self, session_id: UUID) -> LearningPlan | None:
        return session_store.get_learning_plan(session_id)

    def _safe_summary(self, session_id: UUID) -> FinalSummaryPayload | None:
        return session_store.get_summary(session_id)

    def _assessment_start_response(self, state: AssessmentRunState | None) -> AssessmentStartResponse | None:
        if state is None:
            return None
        questions = [item for item in [state.current_question, *state.pending_questions] if item is not None]
        return AssessmentStartResponse(
            assessment_id=state.assessment_id,
            status=state.status,
            questions=questions,
            current_question=state.current_question,
            progress=state.progress,
        )

    def _assessment_complete_response(
        self,
        state: AssessmentRunState | None,
    ) -> AssessmentCompleteResponse | None:
        if state is None or state.status != "completed":
            return None
        return AssessmentCompleteResponse(
            assessment_id=state.assessment_id,
            status=state.status,
            skill_scores=state.skill_scores,
            overall_assessment_summary="Assessment completed.",
        )

    def _available_actions(self, status: SessionStatus) -> list[str]:
        mapping = {
            SessionStatus.CREATED: ["intake"],
            SessionStatus.DOCUMENTS_UPLOADED: ["analysis"],
            SessionStatus.ANALYSIS_COMPLETED: ["assessment_start", "learning_plan", "summary"],
            SessionStatus.ASSESSMENT_IN_PROGRESS: ["assessment_answer", "assessment_complete", "state"],
            SessionStatus.ASSESSMENT_COMPLETED: ["learning_plan", "summary", "state"],
            SessionStatus.LEARNING_PLAN_GENERATED: ["summary", "state"],
            SessionStatus.SUMMARY_GENERATED: ["state"],
        }
        return mapping.get(status, ["state"])
