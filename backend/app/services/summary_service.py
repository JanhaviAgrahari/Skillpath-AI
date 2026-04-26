from statistics import mean
from uuid import UUID, uuid4

from app.core.exceptions import ResourceNotFoundError
from app.repositories.session_store import session_store
from app.schemas.learning_plan import LearningPlan
from app.schemas.common import ReportFit
from app.schemas.summary import (
    AssessmentSummary,
    CandidateProfileSummary,
    ExportPayload,
    FinalSummaryPayload,
    LearningPlanSummary,
    RoleSummary,
    SkillAnalysisSummary,
    SummaryHighlights,
)


class SummaryService:
    """Aggregates analysis, assessment, and planning outputs into one report."""

    async def generate_summary(self, session_id: UUID) -> FinalSummaryPayload:
        session = session_store.get_session(session_id)
        if session is None:
            raise ResourceNotFoundError(f"Session '{session_id}' was not found.")

        analysis = session_store.get_analysis(session_id)
        if analysis is None:
            raise ResourceNotFoundError("Run skill analysis before generating a summary.")

        learning_plan = session_store.get_learning_plan(session_id)
        assessment = session_store.get_assessment_run(session_id)

        fit = self._fit_from_label(analysis.result.role_match_label)
        strongest_skills = [item.skill.canonical_name for item in analysis.result.strong_matches[:5]]
        biggest_gaps = [item.skill.canonical_name for item in analysis.result.missing_skills[:5]]

        assessment_scores = assessment.skill_scores if assessment else []
        assessment_average = round(mean(score.average_score for score in assessment_scores), 2) if assessment_scores else 0.0
        assessment_summary = AssessmentSummary(
            overall_average_score=assessment_average,
            scores=assessment_scores,
            explanation=(
                summarize_assessment_scores(assessment_scores)
                if assessment_scores
                else "Assessment has not been completed yet, so the report uses only document-based analysis."
            ),
        )

        learning_summary = LearningPlanSummary(
            total_weeks=len(learning_plan.milestones) if learning_plan else 1,
            total_hours=learning_plan.overview.estimated_total_hours if learning_plan else 1,
            top_milestones=learning_plan.milestones[:3] if learning_plan else [],
            explanation=(
                learning_plan.overview.rationale
                if learning_plan
                else "Learning plan has not been generated yet."
            ),
        )

        payload = FinalSummaryPayload(
            summary_id=uuid4(),
            status="generated",
            candidate_profile=CandidateProfileSummary(
                candidate_name=session_store.get_resume(session_id)["parsed_data"].full_name
                if session_store.get_resume(session_id)
                else None,
                target_role=session["target_role"],
                current_fit=fit,
                experience_level=session["experience_level"],
            ),
            role_summary=RoleSummary(
                target_role=session["target_role"],
                overall_match_score=analysis.result.role_match_score,
                fit_label=fit,
                explanation=analysis.result.explanation_summary,
            ),
            highlights=SummaryHighlights(
                strongest_skills=strongest_skills,
                main_gaps=biggest_gaps,
            ),
            skill_analysis_summary=SkillAnalysisSummary(
                strong_matches=strongest_skills,
                partial_matches=[item.skill.canonical_name for item in analysis.result.partial_matches[:5]],
                missing_skills=biggest_gaps,
                adjacent_skills=[item.skill.canonical_name for item in analysis.result.adjacent_skills[:5]],
                explanation=analysis.result.explanation_summary,
            ),
            assessment_summary=assessment_summary,
            learning_plan_summary=learning_summary,
            recommended_next_steps=self._recommended_next_steps(
                biggest_gaps=biggest_gaps,
                strongest_skills=strongest_skills,
                learning_plan=learning_plan,
            ),
            export_ready=True,
        )
        session_store.set_summary(session_id, payload)
        return payload

    async def get_summary(self, session_id: UUID) -> FinalSummaryPayload:
        summary = session_store.get_summary(session_id)
        if summary is not None:
            return summary
        return await self.generate_summary(session_id)

    async def export_summary(self, session_id: UUID) -> ExportPayload:
        summary = await self.get_summary(session_id)
        return ExportPayload(
            session_id=session_id,
            report=summary,
            export_metadata={
                "format_version": "1.0",
                "pdf_ready_sections": [
                    "candidate_profile",
                    "role_summary",
                    "skill_analysis_summary",
                    "assessment_summary",
                    "learning_plan_summary",
                    "recommended_next_steps",
                ],
            },
        )

    @staticmethod
    def _fit_from_label(label: str) -> ReportFit:
        if label == "strong_fit":
            return ReportFit.STRONG_FIT
        if label in {"good_fit", "partial_fit"}:
            return ReportFit.PARTIAL_FIT
        return ReportFit.NEEDS_UPSKILLING

    @staticmethod
    def _recommended_next_steps(
        biggest_gaps: list[str],
        strongest_skills: list[str],
        learning_plan: LearningPlan | None,
    ) -> list[str]:
        steps = []
        if biggest_gaps:
            steps.append(f"Prioritize closing the top gap in {biggest_gaps[0]} first.")
        if strongest_skills:
            steps.append(f"Lead with {strongest_skills[0]} in interviews and project walkthroughs.")
        if learning_plan and learning_plan.milestones:
            first = learning_plan.milestones[0]
            steps.append(f"Start with {first.focus} and complete the first milestone deliverables this week.")
        steps.append("Re-run the assessment after the first two milestones to measure improvement.")
        return steps[:6]


def summarize_assessment_scores(skill_scores: list) -> str:
    strongest = max(skill_scores, key=lambda item: item.average_score)
    weakest = min(skill_scores, key=lambda item: item.average_score)
    return (
        f"Assessment results show the strongest demonstrated area is {strongest.skill_name} at {strongest.average_score}/10, "
        f"while {weakest.skill_name} needs the most reinforcement at {weakest.average_score}/10."
    )
