from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.common import (
    DocumentType,
    InputSourceType,
    SessionStatus,
    StepName,
    StrictBaseModel,
)


class SessionCreateRequest(StrictBaseModel):
    user_name: str | None = Field(default=None, min_length=1, max_length=120)
    target_role: str = Field(min_length=2, max_length=120)
    experience_level: str | None = Field(default=None, min_length=2, max_length=40)


class SessionPayload(StrictBaseModel):
    session_id: UUID
    status: SessionStatus
    current_step: StepName
    created_at: datetime


class ResumeUploadMetadata(StrictBaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str | None = Field(default=None, max_length=100)
    file_size_bytes: int | None = Field(default=None, ge=0)


class JobDescriptionInput(StrictBaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    company_name: str | None = Field(default=None, min_length=2, max_length=120)
    raw_text: str = Field(min_length=20, max_length=30000)


class ParsedResumeData(StrictBaseModel):
    source_type: InputSourceType
    full_name: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    summary: str | None = Field(default=None, max_length=3000)
    total_experience_years: float | None = Field(default=None, ge=0, le=60)
    skills: list[str] = Field(default_factory=list, max_length=200)
    education: list[str] = Field(default_factory=list, max_length=50)
    certifications: list[str] = Field(default_factory=list, max_length=50)
    projects: list[str] = Field(default_factory=list, max_length=100)
    normalization_notes: list[str] = Field(default_factory=list, max_length=20)
    raw_text: str = Field(min_length=1)
    normalized_text: str = Field(min_length=1)


class ParsedJobDescriptionData(StrictBaseModel):
    source_type: InputSourceType = InputSourceType.TEXT
    title: str | None = Field(default=None, max_length=200)
    company_name: str | None = Field(default=None, max_length=120)
    summary: str | None = Field(default=None, max_length=3000)
    required_skills: list[str] = Field(default_factory=list, max_length=200)
    preferred_skills: list[str] = Field(default_factory=list, max_length=200)
    responsibilities: list[str] = Field(default_factory=list, max_length=100)
    qualifications: list[str] = Field(default_factory=list, max_length=100)
    normalization_notes: list[str] = Field(default_factory=list, max_length=20)
    raw_text: str = Field(min_length=1)
    normalized_text: str = Field(min_length=1)


class DocumentPayload(StrictBaseModel):
    document_id: UUID
    document_type: DocumentType
    filename: str | None = Field(default=None, max_length=255)
    parsed_text_available: bool = False


class SessionDetailResponse(StrictBaseModel):
    session_id: UUID
    target_role: str | None = Field(default=None, max_length=120)
    status: SessionStatus
    current_step: StepName


class ResumeIngestResponse(StrictBaseModel):
    session_id: UUID
    document_id: UUID
    document_type: DocumentType = DocumentType.RESUME
    source_type: InputSourceType
    filename: str | None = Field(default=None, max_length=255)
    parsed_data: ParsedResumeData
    status: SessionStatus


class JobDescriptionSubmissionRequest(StrictBaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    company_name: str | None = Field(default=None, min_length=2, max_length=120)
    raw_text: str = Field(min_length=20, max_length=30000)


class JobDescriptionIngestResponse(StrictBaseModel):
    session_id: UUID
    document_id: UUID
    document_type: DocumentType = DocumentType.JOB_DESCRIPTION
    source_type: InputSourceType = InputSourceType.TEXT
    parsed_data: ParsedJobDescriptionData
    status: SessionStatus
