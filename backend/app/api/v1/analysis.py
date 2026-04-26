from uuid import UUID

from fastapi import APIRouter

from app.schemas.analysis import AnalysisResponse, AnalysisRunRequest, CompleteAnalysisResponse
from app.schemas.common import ApiResponse
from app.services.analysis_service import AnalysisService

router = APIRouter()
service = AnalysisService()


@router.post("/{session_id}/analysis/run", response_model=ApiResponse[AnalysisResponse])
async def run_analysis(session_id: UUID, payload: AnalysisRunRequest) -> ApiResponse[AnalysisResponse]:
    response = await service.run_analysis(session_id, payload)
    return ApiResponse(data=response)


@router.get("/{session_id}/analysis", response_model=ApiResponse[AnalysisResponse])
async def get_analysis(session_id: UUID) -> ApiResponse[AnalysisResponse]:
    response = await service.get_analysis(session_id)
    return ApiResponse(data=response)


@router.get("/{session_id}/analysis/complete", response_model=ApiResponse[CompleteAnalysisResponse])
async def get_complete_analysis(session_id: UUID) -> ApiResponse[CompleteAnalysisResponse]:
    response = await service.get_complete_analysis(session_id)
    return ApiResponse(data=response)
