import pytest

from app.schemas.analysis import AnalysisRunRequest
from app.schemas.assessment import AssessmentStartRequest, UserAnswer
from app.schemas.learning_plan import LearningPlanRequest
from app.services.analysis_service import AnalysisService
from app.services.assessment_service import AssessmentService
from app.services.learning_plan_service import LearningPlanService
from app.services.skill_extraction_service import SkillExtractionService
from tests.helpers import seed_documents


@pytest.mark.asyncio
async def test_learning_plan_prioritizes_missing_skills(monkeypatch, seeded_session, sample_payloads):
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

    assessment = AssessmentService()
    start = await assessment.start_assessment(
        seeded_session.session_id,
        AssessmentStartRequest(skills_to_assess=["Docker"], questions_per_skill=1),
    )
    await assessment.submit_answer(
        seeded_session.session_id,
        UserAnswer(
            question_id=start.current_question.question_id,
            answer_text="I know Docker images and containers a little, but I have not used compose much in production.",
        ),
    )

    plan = await LearningPlanService().generate_plan(
        seeded_session.session_id,
        LearningPlanRequest(weeks=4, hours_per_week=5, intensity="standard", preferred_learning_style="project_based"),
    )

    assert plan.status == "generated"
    assert len(plan.milestones) == 4
    assert plan.overview.prioritized_skills
    assert plan.milestones[0].resources
    assert plan.overview.estimated_total_hours >= 4


@pytest.mark.asyncio
async def test_learning_plan_requires_analysis(seeded_session):
    with pytest.raises(Exception):
        await LearningPlanService().generate_plan(
            seeded_session.session_id,
            LearningPlanRequest(weeks=2, hours_per_week=4),
        )
