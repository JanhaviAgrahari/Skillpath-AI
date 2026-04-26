from uuid import UUID

from app.schemas.analysis import AnalysisResponse, AnalysisRunRequest, CompleteAnalysisResponse
from app.services.skill_extraction_service import SkillExtractionService


class AnalysisService:
    def __init__(self) -> None:
        self.skill_extraction_service = SkillExtractionService()

    async def run_analysis(self, session_id: UUID, payload: AnalysisRunRequest) -> AnalysisResponse:
        return await self.skill_extraction_service.analyze_session(session_id, payload)

    async def get_analysis(self, session_id: UUID) -> AnalysisResponse:
        return await self.skill_extraction_service.get_analysis(session_id)

    async def get_complete_analysis(self, session_id: UUID) -> CompleteAnalysisResponse:
        return await self.skill_extraction_service.get_complete_analysis(session_id)
