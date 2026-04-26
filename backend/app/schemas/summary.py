from uuid import UUID

from pydantic import Field

from app.schemas.common import ReportFit, StrictBaseModel
from app.schemas.assessment import SkillAssessmentScore
from app.schemas.learning_plan import LearningPlanMilestone


class RoleSummary(StrictBaseModel):
    target_role: str = Field(min_length=1, max_length=120)
    overall_match_score: float = Field(ge=0, le=100)
    fit_label: ReportFit
    explanation: str = Field(min_length=1, max_length=1500)


class SummaryHighlights(StrictBaseModel):
    strongest_skills: list[str] = Field(default_factory=list, max_length=20)
    main_gaps: list[str] = Field(default_factory=list, max_length=20)


class CandidateProfileSummary(StrictBaseModel):
    candidate_name: str | None = Field(default=None, max_length=120)
    target_role: str = Field(min_length=1, max_length=120)
    current_fit: ReportFit
    experience_level: str | None = Field(default=None, max_length=40)


class SkillAnalysisSummary(StrictBaseModel):
    strong_matches: list[str] = Field(default_factory=list, max_length=20)
    partial_matches: list[str] = Field(default_factory=list, max_length=20)
    missing_skills: list[str] = Field(default_factory=list, max_length=20)
    adjacent_skills: list[str] = Field(default_factory=list, max_length=20)
    explanation: str = Field(min_length=1, max_length=1500)


class AssessmentSummary(StrictBaseModel):
    overall_average_score: float = Field(ge=0, le=10)
    scores: list[SkillAssessmentScore] = Field(default_factory=list, max_length=100)
    explanation: str = Field(min_length=1, max_length=1500)


class LearningPlanSummary(StrictBaseModel):
    total_weeks: int = Field(ge=1, le=52)
    total_hours: int = Field(ge=1, le=500)
    top_milestones: list[LearningPlanMilestone] = Field(default_factory=list, max_length=10)
    explanation: str = Field(min_length=1, max_length=1500)


class FinalSummaryPayload(StrictBaseModel):
    summary_id: UUID
    status: str = Field(min_length=1, max_length=50)
    candidate_profile: CandidateProfileSummary
    role_summary: RoleSummary
    highlights: SummaryHighlights
    skill_analysis_summary: SkillAnalysisSummary
    assessment_summary: AssessmentSummary
    learning_plan_summary: LearningPlanSummary
    recommended_next_steps: list[str] = Field(default_factory=list, max_length=20)
    export_ready: bool = False


class ExportPayload(StrictBaseModel):
    session_id: UUID
    export_format: str = Field(default="json", pattern="^(json)$")
    report: FinalSummaryPayload
    export_metadata: dict = Field(default_factory=dict)
