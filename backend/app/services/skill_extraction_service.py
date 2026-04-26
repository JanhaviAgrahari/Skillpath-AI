from uuid import UUID

from pydantic import Field

from app.core.exceptions import LLMOutputError, ResourceNotFoundError
from app.repositories.session_store import session_store
from app.schemas.analysis import (
    AnalysisResponse,
    AnalysisRunRequest,
    CompleteAnalysisResponse,
    GapAnalysisResult,
    SkillGapItem,
    SkillItem,
)
from app.schemas.common import MatchStrength, ProficiencyLevel, SkillCategory, StrictBaseModel
from app.services.llm_service import LLMService
from app.utils.analysis_scoring import compute_role_match_score, role_match_label
from app.utils.prompt_loader import load_prompt_template
from app.utils.skill_catalog import SKILL_DEFINITIONS
from app.utils.skill_matching import build_gap_item, similarity_score
from app.utils.text_normalizer import normalize_skill_token, normalize_whitespace


class SkillExtractionLLMOutput(StrictBaseModel):
    resume_skills: list[str] = Field(default_factory=list)
    jd_required_skills: list[str] = Field(default_factory=list)
    jd_preferred_skills: list[str] = Field(default_factory=list)


class SkillExtractionService:
    def __init__(self) -> None:
        self.llm_service = LLMService()

    async def analyze_session(self, session_id: UUID, config: AnalysisRunRequest | None = None) -> AnalysisResponse:
        session = session_store.get_session(session_id)
        if session is None:
            raise ResourceNotFoundError(f"Session '{session_id}' was not found.")

        resume_entry = session_store.get_resume(session_id)
        jd_entry = session_store.get_job_description(session_id)
        if resume_entry is None:
            raise ResourceNotFoundError("Resume has not been uploaded for this session.")
        if jd_entry is None:
            raise ResourceNotFoundError("Job description has not been submitted for this session.")

        resume_text = resume_entry["parsed_data"].normalized_text
        jd_data = jd_entry["parsed_data"]
        jd_text = jd_data.normalized_text

        deterministic_resume_skills = self._extract_skills_deterministically(resume_text)
        deterministic_jd_skills = self._extract_skills_deterministically(jd_text)
        llm_output = await self._extract_with_llm(resume_text=resume_text, jd_text=jd_text)

        merged_resume_skills = self._merge_skill_sources(
            deterministic_skills=deterministic_resume_skills,
            llm_skills=llm_output.resume_skills if llm_output else [],
            source_text=resume_text,
        )
        merged_jd_skills = self._merge_skill_sources(
            deterministic_skills=deterministic_jd_skills + jd_data.required_skills + jd_data.preferred_skills,
            llm_skills=(llm_output.jd_required_skills + llm_output.jd_preferred_skills) if llm_output else [],
            source_text=jd_text,
        )

        result = self._build_gap_analysis(merged_resume_skills, merged_jd_skills)
        if config is not None and not config.include_adjacent_skills:
            result = result.model_copy(update={"adjacent_skills": []})
        response = AnalysisResponse(
            session_id=session_id,
            analysis_status="completed",
            result=result,
            parsing_ready=True,
        )
        session_store.set_analysis(session_id, response)
        return response

    async def get_analysis(self, session_id: UUID) -> AnalysisResponse:
        session = session_store.get_session(session_id)
        if session is None:
            raise ResourceNotFoundError(f"Session '{session_id}' was not found.")

        result = session_store.get_analysis(session_id)
        if result is not None:
            return result
        return AnalysisResponse(
            session_id=session_id,
            analysis_status="not_started",
            result=GapAnalysisResult(),
            parsing_ready=bool(session_store.get_resume(session_id) and session_store.get_job_description(session_id)),
        )

    async def get_complete_analysis(self, session_id: UUID) -> CompleteAnalysisResponse:
        session = session_store.get_session(session_id)
        if session is None:
            raise ResourceNotFoundError(f"Session '{session_id}' was not found.")

        analysis = await self.get_analysis(session_id)
        resume_entry = session_store.get_resume(session_id)
        jd_entry = session_store.get_job_description(session_id)
        return CompleteAnalysisResponse(
            session_id=session_id,
            analysis_status=analysis.analysis_status,
            parsing_ready=analysis.parsing_ready,
            resume_snapshot=resume_entry["parsed_data"].model_dump() if resume_entry else {},
            jd_snapshot=jd_entry["parsed_data"].model_dump() if jd_entry else {},
            result=analysis.result,
        )

    async def _extract_with_llm(self, resume_text: str, jd_text: str) -> SkillExtractionLLMOutput | None:
        prompt = load_prompt_template("skill_extraction.txt").format(
            resume_text=resume_text[:12000],
            jd_text=jd_text[:12000],
        )
        try:
            return await self.llm_service.generate_structured_output(
                prompt_name="skill_extraction",
                prompt=prompt,
                response_model=SkillExtractionLLMOutput,
            )
        except LLMOutputError:
            return None

    def _extract_skills_deterministically(self, text: str) -> list[SkillItem]:
        normalized_text = normalize_whitespace(text).lower()
        extracted: list[SkillItem] = []
        seen: set[str] = set()
        for definition in SKILL_DEFINITIONS.values():
            aliases = definition["aliases"]
            if any(alias in normalized_text for alias in aliases):
                canonical_name = str(definition["canonical_name"])
                if canonical_name in seen:
                    continue
                seen.add(canonical_name)
                extracted.append(
                    SkillItem(
                        name=canonical_name,
                        canonical_name=canonical_name,
                        category=definition["category"],
                        proficiency=ProficiencyLevel.UNKNOWN,
                        confidence=0.72,
                        evidence=[alias for alias in aliases if alias in normalized_text][:3],
                    )
                )
        return extracted

    def _merge_skill_sources(
        self,
        deterministic_skills: list[SkillItem] | list[str],
        llm_skills: list[str],
        source_text: str,
    ) -> list[SkillItem]:
        merged: dict[str, SkillItem] = {}
        for item in deterministic_skills:
            skill = item if isinstance(item, SkillItem) else self._normalize_to_skill_item(item, source_text, 0.6)
            merged[skill.canonical_name] = skill

        for raw_skill in llm_skills:
            skill = self._normalize_to_skill_item(raw_skill, source_text, 0.82)
            existing = merged.get(skill.canonical_name)
            if existing is None or skill.confidence > existing.confidence:
                merged[skill.canonical_name] = skill
        return sorted(merged.values(), key=lambda skill: skill.canonical_name)

    def _normalize_to_skill_item(self, raw_skill: str, source_text: str, confidence: float) -> SkillItem:
        token = normalize_skill_token(raw_skill)
        for definition in SKILL_DEFINITIONS.values():
            aliases = [normalize_skill_token(alias) for alias in definition["aliases"]]
            if token in aliases or token == normalize_skill_token(str(definition["canonical_name"])):
                canonical_name = str(definition["canonical_name"])
                return SkillItem(
                    name=raw_skill.strip() or canonical_name,
                    canonical_name=canonical_name,
                    category=definition["category"],
                    proficiency=ProficiencyLevel.UNKNOWN,
                    confidence=confidence,
                    evidence=self._collect_evidence(source_text, aliases),
                )

        title_name = raw_skill.strip().title()
        return SkillItem(
            name=title_name,
            canonical_name=title_name,
            category=SkillCategory.OTHER,
            proficiency=ProficiencyLevel.UNKNOWN,
            confidence=round(min(max(confidence, 0.45), 0.95), 2),
            evidence=[raw_skill.strip()] if raw_skill.strip() else [],
        )

    @staticmethod
    def _collect_evidence(source_text: str, aliases: list[str]) -> list[str]:
        lowered = source_text.lower()
        return [alias for alias in aliases if alias in lowered][:3]

    def _build_gap_analysis(self, resume_skills: list[SkillItem], jd_skills: list[SkillItem]) -> GapAnalysisResult:
        strong_matches: list[SkillGapItem] = []
        partial_matches: list[SkillGapItem] = []
        missing_skills: list[SkillGapItem] = []
        adjacent_skills: list[SkillGapItem] = []

        resume_map = {skill.canonical_name.lower(): skill for skill in resume_skills}
        adjacent_seen: set[str] = set()

        for jd_skill in jd_skills:
            exact = resume_map.get(jd_skill.canonical_name.lower())
            if exact:
                strong_matches.append(
                    build_gap_item(
                        skill=jd_skill,
                        match_strength=MatchStrength.STRONG,
                        score=round((exact.confidence + jd_skill.confidence) / 2, 2),
                        reason="The skill appears in both the resume and the job description.",
                        mapped_to=exact.canonical_name,
                    )
                )
                continue

            partial = self._find_partial_match(jd_skill, resume_skills)
            if partial:
                partial_matches.append(
                    build_gap_item(
                        skill=jd_skill,
                        match_strength=MatchStrength.PARTIAL,
                        score=partial[1],
                        reason="A closely related or transferable skill was found in the resume.",
                        mapped_to=partial[0].canonical_name,
                    )
                )
                continue

            missing_skills.append(
                build_gap_item(
                    skill=jd_skill,
                    match_strength=MatchStrength.MISSING,
                    score=0.0,
                    reason="The required skill was not found in the resume.",
                )
            )
            for adjacent_name in self._adjacent_names_for_skill(jd_skill.canonical_name):
                key = adjacent_name.lower()
                if key in adjacent_seen or key in resume_map:
                    continue
                adjacent_seen.add(key)
                adjacent_skills.append(
                    build_gap_item(
                        skill=self._normalize_to_skill_item(adjacent_name, adjacent_name, 0.55),
                        match_strength=MatchStrength.ADJACENT,
                        score=0.55,
                        reason="This related skill can help bridge the missing requirement faster.",
                    )
                )

        assessment_recommendations = [
            item.skill.canonical_name
            for item in (missing_skills + partial_matches + strong_matches[:2])[:8]
        ]
        match_score = compute_role_match_score(
            strong_count=len(strong_matches),
            partial_count=len(partial_matches),
            missing_count=len(missing_skills),
            total_jd_skills=len(jd_skills),
        )
        label = role_match_label(match_score)
        explanation_summary = self._build_explanation_summary(
            strong_matches=strong_matches,
            partial_matches=partial_matches,
            missing_skills=missing_skills,
            match_score=match_score,
            label=label,
        )

        return GapAnalysisResult(
            resume_skills=resume_skills,
            jd_skills=jd_skills,
            strong_matches=strong_matches,
            partial_matches=partial_matches,
            missing_skills=missing_skills,
            adjacent_skills=adjacent_skills,
            assessment_recommendations=assessment_recommendations,
            role_match_score=match_score,
            role_match_label=label,
            explanation_summary=explanation_summary,
        )

    def _find_partial_match(self, jd_skill: SkillItem, resume_skills: list[SkillItem]) -> tuple[SkillItem, float] | None:
        best_match: tuple[SkillItem, float] | None = None
        jd_adjacent = {name.lower() for name in self._adjacent_names_for_skill(jd_skill.canonical_name)}
        for resume_skill in resume_skills:
            ratio = similarity_score(jd_skill.canonical_name, resume_skill.canonical_name)
            adjacent_bonus = 0.12 if resume_skill.canonical_name.lower() in jd_adjacent else 0.0
            total_score = round(min(ratio + adjacent_bonus, 0.89), 2)
            if total_score >= 0.45 and (best_match is None or total_score > best_match[1]):
                best_match = (resume_skill, total_score)
        return best_match

    def _adjacent_names_for_skill(self, canonical_name: str) -> list[str]:
        normalized = normalize_skill_token(canonical_name)
        for definition in SKILL_DEFINITIONS.values():
            if normalize_skill_token(str(definition["canonical_name"])) == normalized:
                return [str(name) for name in definition.get("adjacent", [])]
        return []

    @staticmethod
    def _build_explanation_summary(
        strong_matches: list[SkillGapItem],
        partial_matches: list[SkillGapItem],
        missing_skills: list[SkillGapItem],
        match_score: float,
        label: str,
    ) -> str:
        strong_names = ", ".join(item.skill.canonical_name for item in strong_matches[:3]) or "no clear strong matches yet"
        partial_names = ", ".join(item.skill.canonical_name for item in partial_matches[:3]) or "no meaningful partial matches"
        missing_names = ", ".join(item.skill.canonical_name for item in missing_skills[:3]) or "no major missing skills"
        return (
            f"Role match score: {match_score} ({label}). "
            f"Strong matches include {strong_names}. "
            f"Partial coverage includes {partial_names}. "
            f"Primary gaps are {missing_names}."
        )
