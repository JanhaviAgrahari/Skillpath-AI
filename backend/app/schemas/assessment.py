from uuid import UUID

from pydantic import Field

from app.schemas.common import AssessmentStatus, DifficultyLevel, ProficiencyLevel, StrictBaseModel


class AssessmentQuestion(StrictBaseModel):
    question_id: UUID
    skill_name: str = Field(min_length=1, max_length=100)
    question_text: str = Field(min_length=10, max_length=1000)
    difficulty: DifficultyLevel
    intent: str = Field(default="skill_validation", max_length=120)
    interviewer_note: str = Field(default="Let's reason through this together.", max_length=1000)
    expected_signals: list[str] = Field(default_factory=list, max_length=10)
    is_follow_up: bool = False
    parent_question_id: UUID | None = None


class AssessmentStartRequest(StrictBaseModel):
    skills_to_assess: list[str] = Field(min_length=1, max_length=30)
    questions_per_skill: int = Field(default=2, ge=1, le=5)
    expected_level: ProficiencyLevel = ProficiencyLevel.INTERMEDIATE


class AssessmentProgress(StrictBaseModel):
    total_questions: int = Field(ge=0)
    answered_questions: int = Field(ge=0)


class AssessmentStartResponse(StrictBaseModel):
    assessment_id: UUID
    status: AssessmentStatus
    questions: list[AssessmentQuestion] = Field(default_factory=list, max_length=100)
    current_question: AssessmentQuestion | None = None
    progress: AssessmentProgress


class UserAnswer(StrictBaseModel):
    question_id: UUID
    answer_text: str = Field(min_length=1, max_length=5000)


class AnswerEvaluationResult(StrictBaseModel):
    score: float = Field(ge=0, le=10)
    proficiency_level: ProficiencyLevel
    confidence: float = Field(ge=0, le=1)
    strengths: list[str] = Field(default_factory=list, max_length=10)
    gaps: list[str] = Field(default_factory=list, max_length=10)
    expected_signals_hit: list[str] = Field(default_factory=list, max_length=10)
    rationale: str = Field(min_length=1, max_length=1000)
    feedback: str = Field(min_length=1, max_length=1000)
    follow_up_needed: bool = False


class AnswerSubmissionResponse(StrictBaseModel):
    assessment_id: UUID
    question_id: UUID
    evaluation: AnswerEvaluationResult
    next_question: AssessmentQuestion | None = None
    progress: AssessmentProgress
    skill_score: float = Field(ge=0, le=10)
    skill_proficiency: ProficiencyLevel


class SkillAssessmentScore(StrictBaseModel):
    skill_name: str = Field(min_length=1, max_length=100)
    average_score: float = Field(ge=0, le=10)
    proficiency_level: ProficiencyLevel
    answered_questions: int = Field(default=0, ge=0)
    latest_feedback: str | None = Field(default=None, max_length=1000)


class AssessmentCompleteResponse(StrictBaseModel):
    assessment_id: UUID
    status: AssessmentStatus
    skill_scores: list[SkillAssessmentScore] = Field(default_factory=list, max_length=100)
    overall_assessment_summary: str = Field(min_length=1, max_length=1500)


class AssessmentRunState(StrictBaseModel):
    assessment_id: UUID
    session_id: UUID
    status: AssessmentStatus
    selected_skills: list[str] = Field(default_factory=list, max_length=30)
    current_question: AssessmentQuestion | None = None
    pending_questions: list[AssessmentQuestion] = Field(default_factory=list, max_length=100)
    answered_questions: list[UUID] = Field(default_factory=list, max_length=200)
    progress: AssessmentProgress
    skill_scores: list[SkillAssessmentScore] = Field(default_factory=list, max_length=100)
