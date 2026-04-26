from uuid import UUID

from pydantic import AnyUrl, Field

from app.schemas.common import PlanIntensity, ResourceType, StrictBaseModel


class LearningResource(StrictBaseModel):
    title: str = Field(min_length=1, max_length=200)
    resource_type: ResourceType
    url: AnyUrl
    provider: str | None = Field(default=None, max_length=120)
    estimated_minutes: int | None = Field(default=None, ge=1, le=10000)
    notes: str | None = Field(default=None, max_length=500)


class LearningPlanMilestone(StrictBaseModel):
    week: int = Field(ge=1, le=52)
    title: str = Field(min_length=1, max_length=200)
    focus: str = Field(min_length=1, max_length=200)
    topics: list[str] = Field(default_factory=list, max_length=20)
    tasks: list[str] = Field(default_factory=list, max_length=20)
    outcomes: list[str] = Field(default_factory=list, max_length=20)
    resources: list[LearningResource] = Field(default_factory=list, max_length=20)
    estimated_hours: int = Field(ge=1, le=100)
    intensity: PlanIntensity = PlanIntensity.STANDARD


class LearningPlanRequest(StrictBaseModel):
    weeks: int = Field(default=6, ge=1, le=52)
    hours_per_week: int = Field(default=6, ge=1, le=40)
    focus_skills: list[str] = Field(default_factory=list, max_length=30)
    preferred_learning_style: str | None = Field(default=None, max_length=50)
    intensity: PlanIntensity = PlanIntensity.STANDARD


class LearningPlanOverview(StrictBaseModel):
    goal: str = Field(min_length=1, max_length=300)
    estimated_total_hours: int = Field(ge=1, le=500)
    intensity: PlanIntensity = PlanIntensity.STANDARD
    prioritized_skills: list[str] = Field(default_factory=list, max_length=20)
    rationale: str = Field(default="Learning roadmap not generated yet.", max_length=1500)


class LearningPlan(StrictBaseModel):
    plan_id: UUID
    status: str = Field(min_length=1, max_length=50)
    overview: LearningPlanOverview
    milestones: list[LearningPlanMilestone] = Field(default_factory=list, max_length=52)
