from enum import Enum
from uuid import UUID

from pydantic import Field

from app.schemas.analysis import CompleteAnalysisResponse
from app.schemas.assessment import (
    AssessmentCompleteResponse,
    AssessmentRunState,
    AssessmentStartResponse,
    AnswerSubmissionResponse,
)
from app.schemas.common import SessionStatus, StepName, StrictBaseModel
from app.schemas.learning_plan import LearningPlan
from app.schemas.setup import JobDescriptionIngestResponse, ResumeIngestResponse, SessionDetailResponse
from app.schemas.summary import FinalSummaryPayload


class WorkflowStep(str, Enum):
    INTAKE = "intake"
    ANALYSIS = "analysis"
    ASSESSMENT_START = "assessment_start"
    ASSESSMENT_ANSWER = "assessment_answer"
    ASSESSMENT_COMPLETE = "assessment_complete"
    LEARNING_PLAN = "learning_plan"
    SUMMARY = "summary"
    STATE = "state"


class WorkflowOrchestrationResponse(StrictBaseModel):
    session_id: UUID
    workflow_step: str = Field(min_length=1, max_length=50)
    session_status: SessionStatus
    current_step: StepName
    available_actions: list[str] = Field(default_factory=list, max_length=20)
    session: SessionDetailResponse | None = None
    resume: ResumeIngestResponse | None = None
    job_description: JobDescriptionIngestResponse | None = None
    analysis: CompleteAnalysisResponse | None = None
    assessment_start: AssessmentStartResponse | None = None
    assessment_state: AssessmentRunState | None = None
    assessment_answer: AnswerSubmissionResponse | None = None
    assessment_complete: AssessmentCompleteResponse | None = None
    learning_plan: LearningPlan | None = None
    summary: FinalSummaryPayload | None = None
