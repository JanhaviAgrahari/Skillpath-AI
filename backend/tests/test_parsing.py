from pathlib import Path

import pytest
from fastapi import UploadFile

from app.core.exceptions import DocumentParsingError
from app.schemas.setup import JobDescriptionSubmissionRequest
from app.services.document_parser_service import DocumentParserService


@pytest.mark.asyncio
async def test_ingest_resume_text_happy_path(seeded_session, sample_payloads):
    service = DocumentParserService()

    result = await service.ingest_resume(
        session_id=seeded_session.session_id,
        resume_text=sample_payloads["resume"]["resume_text"],
    )

    assert result.parsed_data.full_name == "Jane Hacker"
    assert result.parsed_data.email == "jane.hacker@example.com"
    assert "Python" in result.parsed_data.skills
    assert result.parsed_data.total_experience_years == 4.0


@pytest.mark.asyncio
async def test_ingest_job_description_happy_path(seeded_session, sample_payloads):
    service = DocumentParserService()

    result = await service.ingest_job_description(
        session_id=seeded_session.session_id,
        payload=JobDescriptionSubmissionRequest(
            title=sample_payloads["job_description"]["title"],
            company_name=sample_payloads["job_description"]["company_name"],
            raw_text=sample_payloads["job_description"]["raw_text"],
        ),
    )

    assert result.parsed_data.title == "Backend Engineer"
    assert "Docker" in result.parsed_data.required_skills
    assert result.parsed_data.source_type == "text"


@pytest.mark.asyncio
async def test_ingest_resume_rejects_short_text(seeded_session):
    service = DocumentParserService()

    with pytest.raises(DocumentParsingError):
        await service.ingest_resume(session_id=seeded_session.session_id, resume_text="too short")


@pytest.mark.asyncio
async def test_ingest_resume_txt_file(seeded_session):
    service = DocumentParserService()
    upload = UploadFile(
        filename="resume.txt",
        file=Path(__file__).resolve().parents[1].joinpath("sample_data", "files", "resume_sample.txt").open("rb"),
    )
    try:
        result = await service.ingest_resume(session_id=seeded_session.session_id, resume_file=upload)
    finally:
        upload.file.close()

    assert result.filename == "resume.txt"
    assert result.parsed_data.full_name == "Jane Hacker"
