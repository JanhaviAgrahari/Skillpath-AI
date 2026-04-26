import json
from uuid import UUID

from fastapi import APIRouter, File, Form, UploadFile

from app.core.exceptions import WorkflowStateError
from app.schemas.common import ApiResponse
from app.schemas.orchestration import WorkflowOrchestrationResponse, WorkflowStep
from app.services.orchestration_service import OrchestrationService

router = APIRouter()
service = OrchestrationService()


@router.post("/workflow/orchestrate", response_model=ApiResponse[WorkflowOrchestrationResponse])
async def orchestrate_workflow(
    workflow_step: WorkflowStep = Form(...),
    session_id: str | None = Form(default=None),
    user_name: str | None = Form(default=None),
    target_role: str | None = Form(default=None),
    experience_level: str | None = Form(default=None),
    resume_text: str | None = Form(default=None),
    resume_file: UploadFile | None = File(default=None),
    job_description_text: str | None = Form(default=None),
    job_title: str | None = Form(default=None),
    company_name: str | None = Form(default=None),
    skills_to_assess_json: str | None = Form(default=None),
    questions_per_skill: int = Form(default=2),
    expected_level: str = Form(default="intermediate"),
    question_id: str | None = Form(default=None),
    answer_text: str | None = Form(default=None),
    plan_weeks: int = Form(default=6),
    plan_hours_per_week: int = Form(default=6),
    plan_intensity: str = Form(default="standard"),
    plan_focus_skills_json: str | None = Form(default=None),
    preferred_learning_style: str | None = Form(default=None),
) -> ApiResponse[WorkflowOrchestrationResponse]:
    response = await service.advance(
        workflow_step=workflow_step.value,
        session_id=_parse_uuid(session_id, "session_id"),
        user_name=user_name,
        target_role=target_role,
        experience_level=experience_level,
        resume_text=resume_text,
        resume_file=resume_file,
        job_description_text=job_description_text,
        job_title=job_title,
        company_name=company_name,
        skills_to_assess=_parse_json_list(skills_to_assess_json),
        questions_per_skill=questions_per_skill,
        expected_level=expected_level,
        question_id=_parse_uuid(question_id, "question_id"),
        answer_text=answer_text,
        plan_weeks=plan_weeks,
        plan_hours_per_week=plan_hours_per_week,
        plan_intensity=plan_intensity,
        plan_focus_skills=_parse_json_list(plan_focus_skills_json),
        preferred_learning_style=preferred_learning_style,
    )
    return ApiResponse(data=response)


def _parse_json_list(value: str | None) -> list[str]:
    if value is None or not value.strip():
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise WorkflowStateError("Expected a valid JSON array string.") from exc
    if not isinstance(parsed, list):
        raise WorkflowStateError("Expected a JSON array string.")
    return [str(item).strip() for item in parsed if str(item).strip()]


def _parse_uuid(value: str | None, field_name: str) -> UUID | None:
    if value is None or not value.strip():
        return None
    try:
        return UUID(value)
    except ValueError as exc:
        raise WorkflowStateError(f"{field_name} must be a valid UUID.") from exc
