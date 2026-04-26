from uuid import UUID

from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.schemas.summary import ExportPayload, FinalSummaryPayload
from app.services.summary_service import SummaryService

router = APIRouter()
service = SummaryService()


@router.post("/{session_id}/summary/generate", response_model=ApiResponse[FinalSummaryPayload])
async def generate_summary(session_id: UUID) -> ApiResponse[FinalSummaryPayload]:
    response = await service.generate_summary(session_id)
    return ApiResponse(data=response)


@router.get("/{session_id}/summary", response_model=ApiResponse[FinalSummaryPayload])
async def get_summary(session_id: UUID) -> ApiResponse[FinalSummaryPayload]:
    response = await service.get_summary(session_id)
    return ApiResponse(data=response)


@router.get("/{session_id}/export", response_model=ApiResponse[ExportPayload])
async def export_summary(session_id: UUID) -> ApiResponse[ExportPayload]:
    payload = await service.export_summary(session_id)
    return ApiResponse(data=payload)
