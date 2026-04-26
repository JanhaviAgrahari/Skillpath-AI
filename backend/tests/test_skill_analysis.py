import pytest

from app.schemas.analysis import AnalysisRunRequest
from app.services.analysis_service import AnalysisService
from app.services.skill_extraction_service import SkillExtractionService
from tests.helpers import seed_documents


@pytest.mark.asyncio
async def test_skill_analysis_builds_expected_categories(monkeypatch, seeded_session, sample_payloads):
    async def no_llm(*args, **kwargs):
        return None

    monkeypatch.setattr(SkillExtractionService, "_extract_with_llm", no_llm)
    await seed_documents(
        seeded_session.session_id,
        sample_payloads["resume"]["resume_text"],
        sample_payloads["job_description"]["raw_text"],
    )

    service = AnalysisService()
    result = await service.run_analysis(
        seeded_session.session_id,
        AnalysisRunRequest(normalize_skills=True, include_adjacent_skills=True),
    )

    strong = {item.skill.canonical_name for item in result.result.strong_matches}
    missing = {item.skill.canonical_name for item in result.result.missing_skills}
    partial = {item.skill.canonical_name for item in result.result.partial_matches}

    assert "Python" in strong
    assert "FastAPI" in strong
    assert "Docker" in missing
    assert "PostgreSQL" in partial or "PostgreSQL" in missing
    assert result.result.role_match_score > 0
    assert "Role match score" in result.result.explanation_summary


@pytest.mark.asyncio
async def test_skill_analysis_can_disable_adjacent_skills(monkeypatch, seeded_session, sample_payloads):
    async def no_llm(*args, **kwargs):
        return None

    monkeypatch.setattr(SkillExtractionService, "_extract_with_llm", no_llm)
    await seed_documents(
        seeded_session.session_id,
        sample_payloads["resume"]["resume_text"],
        sample_payloads["job_description"]["raw_text"],
    )

    service = AnalysisService()
    result = await service.run_analysis(
        seeded_session.session_id,
        AnalysisRunRequest(normalize_skills=True, include_adjacent_skills=False),
    )

    assert result.result.adjacent_skills == []
