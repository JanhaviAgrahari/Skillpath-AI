import pytest

from app.core.exceptions import ResourceNotFoundError
from app.schemas.analysis import AnalysisRunRequest
from app.schemas.assessment import AssessmentStartRequest, UserAnswer
from app.services.analysis_service import AnalysisService
from app.services.assessment_service import AssessmentService
from app.services.skill_extraction_service import SkillExtractionService
from tests.helpers import seed_documents


@pytest.mark.asyncio
async def test_assessment_happy_path_with_follow_up(monkeypatch, seeded_session, sample_payloads):
    async def no_llm(*args, **kwargs):
        return None

    monkeypatch.setattr(SkillExtractionService, "_extract_with_llm", no_llm)
    monkeypatch.setattr(AssessmentService, "_generate_questions_with_llm", no_llm)
    monkeypatch.setattr(AssessmentService, "_evaluate_with_llm", no_llm)

    await seed_documents(
        seeded_session.session_id,
        sample_payloads["resume"]["resume_text"],
        sample_payloads["job_description"]["raw_text"],
    )
    await AnalysisService().run_analysis(
        seeded_session.session_id,
        AnalysisRunRequest(normalize_skills=True, include_adjacent_skills=True),
    )

    service = AssessmentService()
    start = await service.start_assessment(
        seeded_session.session_id,
        AssessmentStartRequest(skills_to_assess=["Docker"], questions_per_skill=2),
    )
    assert start.current_question is not None

    answer = await service.submit_answer(
        seeded_session.session_id,
        UserAnswer(
            question_id=start.current_question.question_id,
            answer_text="I would start with a Dockerfile and container image, but I am not yet confident about compose or environment variables.",
        ),
    )

    assert answer.skill_score >= 0
    assert answer.skill_proficiency in {"unknown", "beginner", "intermediate", "advanced", "expert"}
    assert answer.next_question is not None


@pytest.mark.asyncio
async def test_assessment_rejects_wrong_question_id(monkeypatch, seeded_session, sample_payloads):
    from uuid import uuid4

    async def no_llm(*args, **kwargs):
        return None

    monkeypatch.setattr(SkillExtractionService, "_extract_with_llm", no_llm)
    monkeypatch.setattr(AssessmentService, "_generate_questions_with_llm", no_llm)
    monkeypatch.setattr(AssessmentService, "_evaluate_with_llm", no_llm)

    await seed_documents(
        seeded_session.session_id,
        sample_payloads["resume"]["resume_text"],
        sample_payloads["job_description"]["raw_text"],
    )
    await AnalysisService().run_analysis(
        seeded_session.session_id,
        AnalysisRunRequest(normalize_skills=True, include_adjacent_skills=True),
    )
    service = AssessmentService()
    await service.start_assessment(
        seeded_session.session_id,
        AssessmentStartRequest(skills_to_assess=["Docker"], questions_per_skill=1),
    )

    with pytest.raises(ResourceNotFoundError):
        await service.submit_answer(
            seeded_session.session_id,
            UserAnswer(question_id=uuid4(), answer_text="Wrong question id"),
        )
