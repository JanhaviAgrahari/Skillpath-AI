from uuid import UUID

from fastapi import APIRouter

from app.schemas.assessment import (
    AssessmentCompleteResponse,
    AssessmentRunState,
    AssessmentStartRequest,
    AssessmentStartResponse,
    AnswerSubmissionResponse,
    UserAnswer,
)
from app.schemas.common import ApiResponse
from app.services.assessment_service import AssessmentService

router = APIRouter()
service = AssessmentService()


@router.post("/{session_id}/assessment/start", response_model=ApiResponse[AssessmentStartResponse])
async def start_assessment(session_id: UUID, payload: AssessmentStartRequest) -> ApiResponse[AssessmentStartResponse]:
    response = await service.start_assessment(session_id, payload)
    return ApiResponse(data=response)


@router.get("/{session_id}/assessment", response_model=ApiResponse[AssessmentRunState])
async def get_assessment(session_id: UUID) -> ApiResponse[AssessmentRunState]:
    response = await service.get_assessment(session_id)
    return ApiResponse(data=response)


@router.post("/{session_id}/assessment/answer", response_model=ApiResponse[AnswerSubmissionResponse])
async def submit_answer(session_id: UUID, payload: UserAnswer) -> ApiResponse[AnswerSubmissionResponse]:
    response = await service.submit_answer(session_id, payload)
    return ApiResponse(data=response)


@router.post("/{session_id}/assessment/complete", response_model=ApiResponse[AssessmentCompleteResponse])
async def complete_assessment(session_id: UUID) -> ApiResponse[AssessmentCompleteResponse]:
    response = await service.complete_assessment(session_id)
    return ApiResponse(data=response)
