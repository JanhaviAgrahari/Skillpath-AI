import re
from uuid import UUID, uuid4

from fastapi import UploadFile

from app.core.exceptions import DocumentParsingError, ResourceNotFoundError
from app.repositories.session_store import session_store
from app.schemas.common import DocumentType, InputSourceType, SessionStatus
from app.schemas.setup import (
    JobDescriptionIngestResponse,
    JobDescriptionSubmissionRequest,
    ParsedJobDescriptionData,
    ParsedResumeData,
    ResumeIngestResponse,
)
from app.utils.file_parser import extract_text_from_resume
from app.utils.text_normalizer import normalize_whitespace, split_bullets


class DocumentParserService:
    async def ingest_resume(
        self,
        session_id: UUID,
        resume_file: UploadFile | None = None,
        resume_text: str | None = None,
    ) -> ResumeIngestResponse:
        session = session_store.get_session(session_id)
        if session is None:
            raise ResourceNotFoundError(f"Session '{session_id}' was not found.")

        if resume_file is None and not resume_text:
            raise DocumentParsingError("Provide either a resume file or resume text.")
        if resume_file is not None and resume_text:
            raise DocumentParsingError("Provide either a resume file or resume text, not both.")

        source_type = InputSourceType.FILE if resume_file is not None else InputSourceType.TEXT
        filename = resume_file.filename if resume_file else None

        if resume_file is not None:
            content = await resume_file.read()
            if not content:
                raise DocumentParsingError("The uploaded resume file is empty.")
            raw_text = extract_text_from_resume(content=content, filename=resume_file.filename)
        else:
            raw_text = normalize_whitespace(resume_text or "")
            if len(raw_text) < 20:
                raise DocumentParsingError("Resume text is too short. Please provide a fuller resume.")

        parsed_data = self._build_resume_payload(raw_text=raw_text, source_type=source_type)
        document_id = uuid4()
        session_store.set_resume(
            session_id,
            payload={
                "document_id": document_id,
                "document_type": DocumentType.RESUME,
                "source_type": source_type,
                "filename": filename,
            },
            parsed_data=parsed_data,
        )
        return ResumeIngestResponse(
            session_id=session_id,
            document_id=document_id,
            source_type=source_type,
            filename=filename,
            parsed_data=parsed_data,
            status=SessionStatus.DOCUMENTS_UPLOADED,
        )

    async def ingest_job_description(
        self,
        session_id: UUID,
        payload: JobDescriptionSubmissionRequest,
    ) -> JobDescriptionIngestResponse:
        session = session_store.get_session(session_id)
        if session is None:
            raise ResourceNotFoundError(f"Session '{session_id}' was not found.")

        normalized_text = normalize_whitespace(payload.raw_text)
        if len(normalized_text) < 20:
            raise DocumentParsingError("Job description text is too short.")

        parsed_data = self._build_job_description_payload(
            raw_text=normalized_text,
            title=payload.title,
            company_name=payload.company_name,
        )
        document_id = uuid4()
        session_store.set_job_description(
            session_id,
            payload={
                "document_id": document_id,
                "document_type": DocumentType.JOB_DESCRIPTION,
                "source_type": InputSourceType.TEXT,
            },
            parsed_data=parsed_data,
        )
        return JobDescriptionIngestResponse(
            session_id=session_id,
            document_id=document_id,
            parsed_data=parsed_data,
            status=SessionStatus.DOCUMENTS_UPLOADED,
        )

    def _build_resume_payload(self, raw_text: str, source_type: InputSourceType) -> ParsedResumeData:
        lines = split_bullets(raw_text)
        email = self._search_first(raw_text, r"[\w.+-]+@[\w-]+\.[\w.-]+")
        phone = self._search_first(raw_text, r"(\+?\d[\d\s().-]{7,}\d)")
        skills = self._extract_inline_list(raw_text, ["skills", "technical skills", "tech stack"])
        education = self._extract_section_lines(raw_text, ["education"])
        certifications = self._extract_section_lines(raw_text, ["certifications", "licenses"])
        projects = self._extract_section_lines(raw_text, ["projects", "project experience"])
        normalization_notes = ["Whitespace normalized", "Section bullets cleaned"]

        return ParsedResumeData(
            source_type=source_type,
            full_name=lines[0][:120] if lines else None,
            email=email,
            phone=phone,
            summary=lines[1][:3000] if len(lines) > 1 else None,
            total_experience_years=self._extract_experience_years(raw_text),
            skills=skills,
            education=education[:50],
            certifications=certifications[:50],
            projects=projects[:100],
            normalization_notes=normalization_notes,
            raw_text=raw_text,
            normalized_text=raw_text,
        )

    def _build_job_description_payload(
        self,
        raw_text: str,
        title: str | None,
        company_name: str | None,
    ) -> ParsedJobDescriptionData:
        required_skills = self._extract_inline_list(raw_text, ["requirements", "required skills", "must have"])
        preferred_skills = self._extract_inline_list(raw_text, ["preferred", "nice to have", "good to have"])
        responsibilities = self._extract_section_lines(raw_text, ["responsibilities", "what you'll do", "role"])
        qualifications = self._extract_section_lines(raw_text, ["qualifications", "requirements"])

        summary = split_bullets(raw_text)[0][:3000] if raw_text else None
        return ParsedJobDescriptionData(
            source_type=InputSourceType.TEXT,
            title=title,
            company_name=company_name,
            summary=summary,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            responsibilities=responsibilities[:100],
            qualifications=qualifications[:100],
            normalization_notes=["Whitespace normalized", "Bullet lists normalized"],
            raw_text=raw_text,
            normalized_text=raw_text,
        )

    @staticmethod
    def _search_first(text: str, pattern: str) -> str | None:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        return match.group(0).strip() if match else None

    @staticmethod
    def _extract_experience_years(text: str) -> float | None:
        match = re.search(r"(\d+(?:\.\d+)?)\+?\s+years?", text, flags=re.IGNORECASE)
        return float(match.group(1)) if match else None

    @staticmethod
    def _extract_inline_list(text: str, headers: list[str]) -> list[str]:
        normalized_lines = split_bullets(text)
        items: list[str] = []
        for line in normalized_lines:
            line_lower = line.lower()
            for header in headers:
                if line_lower.startswith(f"{header}:"):
                    values = line.split(":", maxsplit=1)[1]
                    items.extend([part.strip() for part in re.split(r",|/|\|", values) if part.strip()])
        return items[:200]

    @staticmethod
    def _extract_section_lines(text: str, headers: list[str]) -> list[str]:
        normalized_lines = split_bullets(text)
        collected: list[str] = []
        capture = False
        for line in normalized_lines:
            lower = line.lower().strip(":")
            if any(lower == header for header in headers):
                capture = True
                continue
            if capture and line.endswith(":") and len(line.split()) <= 4:
                break
            if capture:
                collected.append(line)
        return collected
