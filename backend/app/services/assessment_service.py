from statistics import mean
from uuid import UUID, uuid4

from pydantic import Field

from app.core.exceptions import LLMOutputError, ResourceNotFoundError
from app.core.logging import get_logger
from app.repositories.session_store import session_store
from app.schemas.assessment import (
    AnswerEvaluationResult,
    AnswerSubmissionResponse,
    AssessmentCompleteResponse,
    AssessmentProgress,
    AssessmentQuestion,
    AssessmentRunState,
    AssessmentStartRequest,
    AssessmentStartResponse,
    SkillAssessmentScore,
    UserAnswer,
)
from app.schemas.common import AssessmentStatus, DifficultyLevel, ProficiencyLevel, StrictBaseModel
from app.services.llm_service import LLMService
from app.utils.assessment_scoring import proficiency_from_score
from app.utils.prompt_loader import load_prompt_template

logger = get_logger(__name__)


# ─── Pydantic models for LLM structured output ──────────────────────────────

class PreviousAnswerEvaluation(StrictBaseModel):
    score: float = Field(ge=0, le=10)
    confidence: float = Field(ge=0, le=1)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    rationale: str = ""
    feedback: str = ""


class AssessmentTurnResponse(StrictBaseModel):
    """The JSON structure the LLM returns on every conversational turn."""
    question_text: str = ""
    skill_name: str = ""
    difficulty: str = "medium"
    interviewer_note: str = ""
    evaluation_of_previous_answer: PreviousAnswerEvaluation | None = None
    is_follow_up: bool = False
    is_complete: bool = False
    skills_covered_so_far: list[str] = Field(default_factory=list)


# ─── Service ─────────────────────────────────────────────────────────────────

class AssessmentService:
    def __init__(self) -> None:
        self.llm_service = LLMService()

    # ── public: start ─────────────────────────────────────────────────────

    async def start_assessment(
        self,
        session_id: UUID,
        payload: AssessmentStartRequest,
    ) -> AssessmentStartResponse:
        analysis = session_store.get_analysis(session_id)
        if analysis is None:
            raise ResourceNotFoundError("Run analysis before starting the assessment.")

        selected_skills = [s.strip() for s in payload.skills_to_assess if s.strip()]
        if not selected_skills:
            raise ResourceNotFoundError("At least one skill is required to start the assessment.")

        # Get resume + JD text for the system prompt
        resume_entry = session_store.get_resume(session_id)
        jd_entry = session_store.get_job_description(session_id)
        resume_text = resume_entry["parsed_data"].normalized_text if resume_entry else "Not available"
        jd_text = jd_entry["parsed_data"].normalized_text if jd_entry else "Not available"

        # Build the system instruction with full context
        system_instruction = load_prompt_template("assessment_system.txt").format(
            resume_text=resume_text[:8000],
            jd_text=jd_text[:8000],
            skills_to_assess=", ".join(selected_skills),
        )

        # Store the system instruction for later turns
        session_store.set_conversation_history(session_id, [])
        # We store system_instruction separately in the session metadata
        session_record = session_store.get_session(session_id)
        if session_record:
            session_record["_system_instruction"] = system_instruction

        # Ask the LLM for the first question (no user answer yet)
        first_user_msg = "Please begin the assessment. Ask me your first question."
        session_store.append_conversation_turn(session_id, "user", first_user_msg)

        llm_response = await self._call_llm(session_id, system_instruction)

        # Save the model's response in conversation history
        session_store.append_conversation_turn(
            session_id, "model", llm_response.model_dump_json()
        )

        # Build the first question object
        first_question = self._to_question(llm_response)

        run_state = AssessmentRunState(
            assessment_id=uuid4(),
            session_id=session_id,
            status=AssessmentStatus.IN_PROGRESS,
            selected_skills=selected_skills,
            current_question=first_question,
            pending_questions=[],
            answered_questions=[],
            progress=AssessmentProgress(
                total_questions=len(selected_skills),
                answered_questions=0,
            ),
            skill_scores=[],
        )
        session_store.set_assessment_run(session_id, run_state)

        return AssessmentStartResponse(
            assessment_id=run_state.assessment_id,
            status=run_state.status,
            questions=[first_question],
            current_question=first_question,
            progress=run_state.progress,
        )

    # ── public: get ───────────────────────────────────────────────────────

    async def get_assessment(self, session_id: UUID) -> AssessmentRunState:
        run_state = session_store.get_assessment_run(session_id)
        if run_state is None:
            raise ResourceNotFoundError("Assessment has not been started for this session.")
        return run_state

    # ── public: submit answer ─────────────────────────────────────────────

    async def submit_answer(
        self,
        session_id: UUID,
        payload: UserAnswer,
    ) -> AnswerSubmissionResponse:
        run_state = session_store.get_assessment_run(session_id)
        if run_state is None:
            raise ResourceNotFoundError("Assessment has not been started for this session.")
        current_question = run_state.current_question
        if current_question is None:
            raise ResourceNotFoundError("There is no active question to answer.")
        if current_question.question_id != payload.question_id:
            raise ResourceNotFoundError("The submitted answer does not match the current assessment question.")

        # Append user answer to conversation history
        session_store.append_conversation_turn(session_id, "user", payload.answer_text)

        # Get the system instruction from the session
        session_record = session_store.get_session(session_id)
        system_instruction = session_record.get("_system_instruction", "") if session_record else ""

        # Call LLM with full conversation history
        llm_response = await self._call_llm(session_id, system_instruction)

        # Save model response to history
        session_store.append_conversation_turn(
            session_id, "model", llm_response.model_dump_json()
        )

        # Extract evaluation
        evaluation = self._to_evaluation(llm_response, current_question.skill_name)

        # Update skill scores
        updated_skill_scores = self._update_skill_scores(
            current_scores=run_state.skill_scores,
            skill_name=current_question.skill_name,
            evaluation=evaluation,
        )

        # Determine next question
        next_question = None
        is_done = llm_response.is_complete

        if not is_done and llm_response.question_text.strip():
            next_question = self._to_question(llm_response)

        answered_questions = [*run_state.answered_questions, current_question.question_id]
        skills_covered = len(set(llm_response.skills_covered_so_far)) if llm_response.skills_covered_so_far else len(answered_questions)
        progress = AssessmentProgress(
            total_questions=max(run_state.progress.total_questions, skills_covered + (1 if next_question else 0)),
            answered_questions=len(answered_questions),
        )

        new_status = AssessmentStatus.COMPLETED if is_done else AssessmentStatus.IN_PROGRESS
        new_state = run_state.model_copy(
            update={
                "current_question": next_question,
                "pending_questions": [],
                "answered_questions": answered_questions,
                "progress": progress,
                "skill_scores": updated_skill_scores,
                "status": new_status,
            }
        )
        if new_status == AssessmentStatus.COMPLETED:
            session_store.complete_assessment_run(session_id, new_state)
        else:
            session_store.set_assessment_run(session_id, new_state)

        skill_score = next(
            (s for s in updated_skill_scores if s.skill_name.lower() == current_question.skill_name.lower()),
            SkillAssessmentScore(
                skill_name=current_question.skill_name,
                average_score=evaluation.score,
                proficiency_level=proficiency_from_score(evaluation.score),
                answered_questions=1,
                latest_feedback=evaluation.feedback,
            ),
        )

        return AnswerSubmissionResponse(
            assessment_id=new_state.assessment_id,
            question_id=payload.question_id,
            evaluation=evaluation,
            next_question=next_question,
            progress=progress,
            skill_score=skill_score.average_score,
            skill_proficiency=skill_score.proficiency_level,
        )

    # ── public: complete ──────────────────────────────────────────────────

    async def complete_assessment(self, session_id: UUID) -> AssessmentCompleteResponse:
        run_state = session_store.get_assessment_run(session_id)
        if run_state is None:
            raise ResourceNotFoundError("Assessment has not been started for this session.")

        summary = self._build_assessment_summary(run_state.skill_scores)
        completed_state = run_state.model_copy(
            update={"status": AssessmentStatus.COMPLETED, "current_question": None}
        )
        session_store.complete_assessment_run(session_id, completed_state)
        return AssessmentCompleteResponse(
            assessment_id=completed_state.assessment_id,
            status=AssessmentStatus.COMPLETED,
            skill_scores=completed_state.skill_scores,
            overall_assessment_summary=summary,
        )

    # ── private: LLM call ─────────────────────────────────────────────────

    async def _call_llm(
        self,
        session_id: UUID,
        system_instruction: str,
    ) -> AssessmentTurnResponse:
        history = session_store.get_conversation_history(session_id)

        try:
            return await self.llm_service.chat(
                system_instruction=system_instruction,
                conversation_history=history,
                response_model=AssessmentTurnResponse,
            )
        except LLMOutputError:
            logger.warning("llm_assessment_chat_failed", extra={"session_id": str(session_id)})
            # Return a graceful fallback if the LLM is completely down
            return AssessmentTurnResponse(
                question_text="I'm having trouble connecting to the assessment engine. Could you please try again in a moment?",
                skill_name="System",
                difficulty="medium",
                interviewer_note="LLM call failed — returning retry message",
                is_complete=False,
            )

    # ── private: conversion helpers ───────────────────────────────────────

    @staticmethod
    def _to_question(llm_resp: AssessmentTurnResponse) -> AssessmentQuestion:
        difficulty_map = {"easy": DifficultyLevel.EASY, "medium": DifficultyLevel.MEDIUM, "hard": DifficultyLevel.HARD}
        return AssessmentQuestion(
            question_id=uuid4(),
            skill_name=llm_resp.skill_name or "General",
            question_text=llm_resp.question_text,
            difficulty=difficulty_map.get(llm_resp.difficulty.lower(), DifficultyLevel.MEDIUM),
            intent="follow_up_probe" if llm_resp.is_follow_up else "skill_validation",
            interviewer_note=llm_resp.interviewer_note or "Let's explore this together.",
            expected_signals=[],
            is_follow_up=llm_resp.is_follow_up,
        )

    @staticmethod
    def _to_evaluation(
        llm_resp: AssessmentTurnResponse,
        skill_name: str,
    ) -> AnswerEvaluationResult:
        ev = llm_resp.evaluation_of_previous_answer
        if ev is None:
            # LLM didn't provide evaluation (shouldn't happen, but safe fallback)
            return AnswerEvaluationResult(
                score=5.0,
                proficiency_level=ProficiencyLevel.INTERMEDIATE,
                confidence=0.5,
                strengths=["Response received"],
                gaps=[],
                expected_signals_hit=[],
                rationale="Evaluation could not be generated for this answer.",
                feedback="Thank you for your response.",
                follow_up_needed=False,
            )
        return AnswerEvaluationResult(
            score=max(0, min(ev.score, 10)),
            proficiency_level=proficiency_from_score(ev.score),
            confidence=max(0, min(ev.confidence, 1)),
            strengths=ev.strengths[:10],
            gaps=ev.gaps[:10],
            expected_signals_hit=[],
            rationale=ev.rationale or "Evaluation provided by the assessment agent.",
            feedback=ev.feedback or "Review your response for areas of improvement.",
            follow_up_needed=llm_resp.is_follow_up,
        )

    # ── private: scoring ──────────────────────────────────────────────────

    def _update_skill_scores(
        self,
        current_scores: list[SkillAssessmentScore],
        skill_name: str,
        evaluation: AnswerEvaluationResult,
    ) -> list[SkillAssessmentScore]:
        score_map = {s.skill_name.lower(): s for s in current_scores}
        existing = score_map.get(skill_name.lower())
        previous_total = (
            existing.average_score * existing.answered_questions
            if existing and existing.answered_questions > 0
            else 0.0
        )
        new_count = (existing.answered_questions if existing else 0) + 1
        updated_avg = round((previous_total + evaluation.score) / new_count, 2)

        updated = [s for s in current_scores if s.skill_name.lower() != skill_name.lower()]
        updated.append(
            SkillAssessmentScore(
                skill_name=skill_name,
                average_score=updated_avg,
                proficiency_level=proficiency_from_score(updated_avg),
                answered_questions=new_count,
                latest_feedback=evaluation.feedback,
            )
        )
        return sorted(updated, key=lambda x: x.skill_name.lower())

    @staticmethod
    def _build_assessment_summary(skill_scores: list[SkillAssessmentScore]) -> str:
        if not skill_scores:
            return "No assessment answers were recorded."
        strongest = max(skill_scores, key=lambda s: s.average_score)
        weakest = min(skill_scores, key=lambda s: s.average_score)
        overall = round(mean(s.average_score for s in skill_scores), 2)
        return (
            f"The candidate's assessment average is {overall}/10. "
            f"Strongest area: {strongest.skill_name} ({strongest.average_score}/10). "
            f"Main improvement area: {weakest.skill_name} ({weakest.average_score}/10)."
        )
