from uuid import UUID

from pydantic import Field

from app.schemas.common import MatchStrength, ProficiencyLevel, SkillCategory, StrictBaseModel


class SkillItem(StrictBaseModel):
    name: str = Field(min_length=1, max_length=100)
    canonical_name: str = Field(min_length=1, max_length=100)
    category: SkillCategory
    proficiency: ProficiencyLevel = ProficiencyLevel.UNKNOWN
    confidence: float = Field(default=0.5, ge=0, le=1)
    years_of_experience: float | None = Field(default=None, ge=0, le=60)
    evidence: list[str] = Field(default_factory=list, max_length=20)


class SkillGapItem(StrictBaseModel):
    skill: SkillItem
    match_strength: MatchStrength
    score: float = Field(ge=0, le=1)
    mapped_to: str | None = Field(default=None, max_length=100)
    reason: str = Field(min_length=1, max_length=500)


class GapAnalysisResult(StrictBaseModel):
    resume_skills: list[SkillItem] = Field(default_factory=list, max_length=300)
    jd_skills: list[SkillItem] = Field(default_factory=list, max_length=300)
    strong_matches: list[SkillGapItem] = Field(default_factory=list, max_length=200)
    partial_matches: list[SkillGapItem] = Field(default_factory=list, max_length=200)
    missing_skills: list[SkillGapItem] = Field(default_factory=list, max_length=200)
    adjacent_skills: list[SkillGapItem] = Field(default_factory=list, max_length=200)
    assessment_recommendations: list[str] = Field(default_factory=list, max_length=50)
    role_match_score: float = Field(default=0, ge=0, le=100)
    role_match_label: str = Field(default="low_fit", max_length=40)
    explanation_summary: str = Field(default="Analysis not generated yet.", max_length=1500)


class AnalysisRunRequest(StrictBaseModel):
    normalize_skills: bool = True
    include_adjacent_skills: bool = True


class AnalysisResponse(StrictBaseModel):
    session_id: UUID
    analysis_status: str
    result: GapAnalysisResult
    parsing_ready: bool = True


class CompleteAnalysisResponse(StrictBaseModel):
    session_id: UUID
    analysis_status: str
    parsing_ready: bool = True
    resume_snapshot: dict = Field(default_factory=dict)
    jd_snapshot: dict = Field(default_factory=dict)
    result: GapAnalysisResult
