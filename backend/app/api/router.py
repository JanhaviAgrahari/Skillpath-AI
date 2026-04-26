from fastapi import APIRouter

from app.api.v1.analysis import router as analysis_router
from app.api.v1.assessment import router as assessment_router
from app.api.v1.health import router as health_router
from app.api.v1.learning_plan import router as learning_plan_router
from app.api.v1.setup import router as setup_router
from app.api.v1.summary import router as summary_router
from app.api.v1.workflow import router as workflow_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(setup_router, prefix="/sessions", tags=["setup"])
api_router.include_router(analysis_router, prefix="/sessions", tags=["analysis"])
api_router.include_router(assessment_router, prefix="/sessions", tags=["assessment"])
api_router.include_router(learning_plan_router, prefix="/sessions", tags=["learning-plan"])
api_router.include_router(summary_router, prefix="/sessions", tags=["summary"])
api_router.include_router(workflow_router, tags=["workflow"])
