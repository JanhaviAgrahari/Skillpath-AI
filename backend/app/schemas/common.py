from datetime import datetime
from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        from_attributes=True,
    )


class DocumentType(str, Enum):
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"


class InputSourceType(str, Enum):
    FILE = "file"
    TEXT = "text"


class SkillCategory(str, Enum):
    TECHNICAL = "technical"
    TOOL = "tool"
    FRAMEWORK = "framework"
    DATABASE = "database"
    CLOUD = "cloud"
    SOFT = "soft"
    DOMAIN = "domain"
    OTHER = "other"


class ProficiencyLevel(str, Enum):
    UNKNOWN = "unknown"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class MatchStrength(str, Enum):
    STRONG = "strong"
    PARTIAL = "partial"
    MISSING = "missing"
    ADJACENT = "adjacent"


class AssessmentStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ResourceType(str, Enum):
    DOCUMENTATION = "documentation"
    COURSE = "course"
    VIDEO = "video"
    ARTICLE = "article"
    PROJECT = "project"
    BOOK = "book"
    OTHER = "other"


class ReportFit(str, Enum):
    STRONG_FIT = "strong_fit"
    PARTIAL_FIT = "partial_fit"
    NEEDS_UPSKILLING = "needs_upskilling"


class PlanIntensity(str, Enum):
    GENTLE = "gentle"
    STANDARD = "standard"
    INTENSIVE = "intensive"


class SessionStatus(str, Enum):
    CREATED = "created"
    DOCUMENTS_UPLOADED = "documents_uploaded"
    ANALYSIS_COMPLETED = "analysis_completed"
    ASSESSMENT_IN_PROGRESS = "assessment_in_progress"
    ASSESSMENT_COMPLETED = "assessment_completed"
    LEARNING_PLAN_GENERATED = "learning_plan_generated"
    SUMMARY_GENERATED = "summary_generated"


class StepName(str, Enum):
    SETUP = "setup"
    ANALYSIS = "analysis"
    ASSESSMENT = "assessment"
    LEARNING_PLAN = "learning_plan"
    SUMMARY = "summary"


class MessageEnvelope(StrictBaseModel):
    code: str = Field(default="ok")
    message: str = Field(default="success")


class ApiResponse(StrictBaseModel, Generic[T]):
    success: bool = True
    message: MessageEnvelope = Field(default_factory=MessageEnvelope)
    data: T
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ApiErrorResponse(StrictBaseModel):
    success: bool = False
    error_code: str
    error_message: str
    details: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
