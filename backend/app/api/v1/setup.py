from uuid import UUID

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.common import ApiResponse
from app.schemas.setup import (
    JobDescriptionIngestResponse,
    JobDescriptionSubmissionRequest,
    ResumeIngestResponse,
    SessionCreateRequest,
    SessionDetailResponse,
    SessionPayload,
)
from app.services.document_parser_service import DocumentParserService
from app.services.setup_service import SetupService

router = APIRouter()
service = SetupService()
document_parser_service = DocumentParserService()


@router.post("", response_model=ApiResponse[SessionPayload])
async def create_session(payload: SessionCreateRequest) -> ApiResponse[SessionPayload]:
    session = await service.create_session(payload)
    return ApiResponse(data=session)


@router.post("/{session_id}/resume", response_model=ApiResponse[ResumeIngestResponse])
async def upload_resume(
    session_id: UUID,
    resume_file: UploadFile | None = File(default=None),
    resume_text: str | None = Form(default=None),
) -> ApiResponse[ResumeIngestResponse]:
    response = await document_parser_service.ingest_resume(
        session_id=session_id,
        resume_file=resume_file,
        resume_text=resume_text,
    )
    return ApiResponse(data=response)


@router.post("/{session_id}/job-description", response_model=ApiResponse[JobDescriptionIngestResponse])
async def submit_job_description(
    session_id: UUID,
    payload: JobDescriptionSubmissionRequest,
) -> ApiResponse[JobDescriptionIngestResponse]:
    response = await document_parser_service.ingest_job_description(session_id=session_id, payload=payload)
    return ApiResponse(data=response)


@router.get("/{session_id}", response_model=ApiResponse[SessionDetailResponse])
async def get_session(session_id: UUID) -> ApiResponse[SessionDetailResponse]:
    session = await service.get_session(session_id)
    return ApiResponse(data=session)
