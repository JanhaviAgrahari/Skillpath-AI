from app.schemas.setup import JobDescriptionSubmissionRequest
from app.services.analysis_service import AnalysisService
from app.services.document_parser_service import DocumentParserService


async def seed_documents(session_id, resume_text: str, job_description_text: str) -> None:
    parser = DocumentParserService()
    await parser.ingest_resume(session_id=session_id, resume_text=resume_text)
    await parser.ingest_job_description(
        session_id=session_id,
        payload=JobDescriptionSubmissionRequest(
            title="Backend Engineer",
            company_name="Acme",
            raw_text=job_description_text,
        ),
    )


async def run_analysis(session_id) -> None:
    service = AnalysisService()
    await service.run_analysis(session_id, payload=type("Payload", (), {"normalize_skills": True, "include_adjacent_skills": True})())
