from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SessionRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "sessions"

    user_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    target_role: Mapped[str | None] = mapped_column(String(120), nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="created")
    current_step: Mapped[str] = mapped_column(String(50), default="setup")


class DocumentRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    document_type: Mapped[str] = mapped_column(String(40))
    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_payload: Mapped[dict] = mapped_column(JSONB, default=dict)


class SkillAnalysisRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "skill_analyses"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    analysis_payload: Mapped[dict] = mapped_column(JSONB, default=dict)


class AssessmentRunRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "assessment_runs"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="not_started")
    questions_payload: Mapped[list] = mapped_column(JSONB, default=list)
    answers_payload: Mapped[list] = mapped_column(JSONB, default=list)
    results_payload: Mapped[dict] = mapped_column(JSONB, default=dict)


class LearningPlanRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "learning_plans"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    plan_payload: Mapped[dict] = mapped_column(JSONB, default=dict)


class SummaryRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "summaries"

    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    summary_payload: Mapped[dict] = mapped_column(JSONB, default=dict)
