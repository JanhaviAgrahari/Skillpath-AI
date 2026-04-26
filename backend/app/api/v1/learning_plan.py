from uuid import UUID

from fastapi import APIRouter

from app.schemas.common import ApiResponse
from app.schemas.learning_plan import LearningPlan, LearningPlanRequest
from app.services.learning_plan_service import LearningPlanService

router = APIRouter()
service = LearningPlanService()


@router.post("/{session_id}/learning-plan/generate", response_model=ApiResponse[LearningPlan])
async def generate_learning_plan(session_id: UUID, payload: LearningPlanRequest) -> ApiResponse[LearningPlan]:
    response = await service.generate_plan(session_id, payload)
    return ApiResponse(data=response)


@router.get("/{session_id}/learning-plan", response_model=ApiResponse[LearningPlan])
async def get_learning_plan(session_id: UUID) -> ApiResponse[LearningPlan]:
    response = await service.get_plan(session_id)
    return ApiResponse(data=response)
