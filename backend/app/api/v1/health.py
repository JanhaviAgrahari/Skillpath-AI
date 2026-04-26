from fastapi import APIRouter

from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("/health", response_model=ApiResponse[dict[str, str]])
async def healthcheck() -> ApiResponse[dict[str, str]]:
    return ApiResponse(data={"status": "ok"})
