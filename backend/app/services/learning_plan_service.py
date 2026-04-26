from uuid import UUID, uuid4

from app.core.exceptions import ResourceNotFoundError
from app.repositories.session_store import session_store
from app.schemas.analysis import SkillGapItem
from app.schemas.assessment import SkillAssessmentScore
from app.schemas.common import PlanIntensity
from app.schemas.learning_plan import (
    LearningPlan,
    LearningPlanMilestone,
    LearningPlanOverview,
    LearningPlanRequest,
    LearningResource,
)
from app.utils.learning_plan_builder import adjusted_hours_per_week, difficulty_weight_from_score, section_hours
from app.utils.learning_resources import RESOURCE_CATALOG


class LearningPlanService:
    async def generate_plan(self, session_id: UUID, payload: LearningPlanRequest) -> LearningPlan:
        session = session_store.get_session(session_id)
        if session is None:
            raise ResourceNotFoundError(f"Session '{session_id}' was not found.")

        analysis = session_store.get_analysis(session_id)
        if analysis is None:
            raise ResourceNotFoundError("Run skill analysis before generating a learning plan.")

        assessment = session_store.get_assessment_run(session_id)
        plan_focus = self._prioritize_skills(
            missing_skills=analysis.result.missing_skills,
            partial_matches=analysis.result.partial_matches,
            adjacent_skills=analysis.result.adjacent_skills,
            selected_skills=payload.focus_skills,
            assessment_scores=assessment.skill_scores if assessment else [],
        )
        if not plan_focus:
            plan_focus = [item.skill.canonical_name for item in analysis.result.missing_skills[:3]]
        if not plan_focus:
            plan_focus = analysis.result.assessment_recommendations[:3]

        hours_per_week = adjusted_hours_per_week(payload.hours_per_week, payload.intensity)
        milestones = self._build_milestones(
            prioritized_skills=plan_focus,
            weeks=payload.weeks,
            hours_per_week=hours_per_week,
            intensity=payload.intensity,
            preferred_learning_style=payload.preferred_learning_style,
        )
        total_hours = sum(milestone.estimated_hours for milestone in milestones)
        overview = LearningPlanOverview(
            goal=f"Close the most important gaps for the {session['target_role']} role with a focused, build-oriented plan.",
            estimated_total_hours=total_hours,
            intensity=payload.intensity,
            prioritized_skills=plan_focus,
            rationale=(
                "The roadmap prioritizes missing and weak skills first, but uses adjacent topics early when they can "
                "reduce ramp-up friction and improve confidence before harder core gaps."
            ),
        )
        plan = LearningPlan(
            plan_id=uuid4(),
            status="generated",
            overview=overview,
            milestones=milestones,
        )
        session_store.set_learning_plan(session_id, plan)
        return plan

    async def get_plan(self, session_id: UUID) -> LearningPlan:
        plan = session_store.get_learning_plan(session_id)
        if plan is None:
            raise ResourceNotFoundError("Learning plan has not been generated for this session.")
        return plan

    def _prioritize_skills(
        self,
        missing_skills: list[SkillGapItem],
        partial_matches: list[SkillGapItem],
        adjacent_skills: list[SkillGapItem],
        selected_skills: list[str],
        assessment_scores: list[SkillAssessmentScore],
    ) -> list[str]:
        score_map = {score.skill_name.lower(): score.average_score for score in assessment_scores}
        selected = {skill.lower() for skill in selected_skills}
        prioritized: list[tuple[int, str]] = []

        for item in missing_skills:
            name = item.skill.canonical_name
            penalty = difficulty_weight_from_score(score_map.get(name.lower()))
            weight = 10 + penalty
            if selected and name.lower() in selected:
                weight += 4
            prioritized.append((weight, name))

        for item in partial_matches:
            name = item.skill.canonical_name
            penalty = difficulty_weight_from_score(score_map.get(name.lower()))
            prioritized.append((7 + penalty, name))

        for item in adjacent_skills[:4]:
            name = item.skill.canonical_name
            prioritized.append((5, name))

        deduped: list[str] = []
        for _, skill_name in sorted(prioritized, key=lambda entry: (-entry[0], entry[1])):
            if skill_name not in deduped:
                deduped.append(skill_name)
        return deduped[:6]

    def _build_milestones(
        self,
        prioritized_skills: list[str],
        weeks: int,
        hours_per_week: int,
        intensity: PlanIntensity,
        preferred_learning_style: str | None,
    ) -> list[LearningPlanMilestone]:
        milestones: list[LearningPlanMilestone] = []
        skill_count = max(1, len(prioritized_skills))
        for week in range(1, weeks + 1):
            skill_name = prioritized_skills[(week - 1) % skill_count]
            resources = self._resources_for_skill(skill_name)
            style_task = (
                "Build a small working project slice that proves the concept."
                if preferred_learning_style == "project_based"
                else "Write short notes and examples to explain the concept back clearly."
            )
            milestones.append(
                LearningPlanMilestone(
                    week=week,
                    title=f"Week {week}: {skill_name} focus",
                    focus=skill_name,
                    topics=self._topics_for_skill(skill_name),
                    tasks=[
                        f"Study the core concepts of {skill_name} with one primary resource.",
                        f"Apply {skill_name} in a backend-relevant exercise or mini-feature.",
                        style_task,
                    ],
                    outcomes=[
                        f"Explain the key trade-offs of {skill_name} in an interview-style answer.",
                        f"Demonstrate {skill_name} in a working backend example.",
                    ],
                    resources=resources,
                    estimated_hours=min(section_hours(hours_per_week, intensity=intensity), 100),
                    intensity=intensity,
                )
            )
        return milestones

    def _resources_for_skill(self, skill_name: str) -> list[LearningResource]:
        return RESOURCE_CATALOG.get(skill_name, RESOURCE_CATALOG.get("Backend Development", []))[:3]

    def _topics_for_skill(self, skill_name: str) -> list[str]:
        topic_map = {
            "Docker": ["images", "containers", "Dockerfile optimization", "environment configuration"],
            "PostgreSQL": ["schema design", "indexes", "query tuning", "transactions"],
            "SQL": ["joins", "aggregation", "indexing", "query optimization"],
            "FastAPI": ["routing", "validation", "dependency injection", "async handlers"],
            "REST APIs": ["resource design", "status codes", "validation", "error handling"],
            "CI/CD": ["automation", "test pipelines", "deployment flow", "rollback awareness"],
            "Kubernetes": ["pods", "services", "deployments", "configuration"],
        }
        return topic_map.get(skill_name, [skill_name, "implementation", "debugging", "trade-offs"])
