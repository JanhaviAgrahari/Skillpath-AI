from io import BytesIO
from pathlib import Path

from app.core.exceptions import DocumentParsingError
from app.utils.text_normalizer import normalize_whitespace

SUPPORTED_RESUME_EXTENSIONS = {".pdf", ".docx", ".txt"}


def get_file_extension(filename: str | None) -> str:
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def extract_text_from_resume(content: bytes, filename: str | None) -> str:
    extension = get_file_extension(filename)
    if extension not in SUPPORTED_RESUME_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_RESUME_EXTENSIONS))
        raise DocumentParsingError(
            f"Unsupported resume file type '{extension or 'unknown'}'. Supported types: {supported}."
        )

    if extension == ".pdf":
        return _extract_pdf_text(content)
    if extension == ".docx":
        return _extract_docx_text(content)
    if extension == ".txt":
        return _extract_txt_text(content)

    raise DocumentParsingError("Unable to determine how to parse the uploaded file.")


def _extract_pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise DocumentParsingError("Failed to parse PDF resume. Please upload a valid PDF file.") from exc

    normalized = normalize_whitespace(text)
    if not normalized:
        raise DocumentParsingError("The uploaded PDF did not contain extractable text.")
    return normalized


def _extract_docx_text(content: bytes) -> str:
    try:
        from docx import Document

        document = Document(BytesIO(content))
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        text = "\n".join(paragraphs)
    except Exception as exc:
        raise DocumentParsingError("Failed to parse DOCX resume. Please upload a valid DOCX file.") from exc

    normalized = normalize_whitespace(text)
    if not normalized:
        raise DocumentParsingError("The uploaded DOCX did not contain extractable text.")
    return normalized


def _extract_txt_text(content: bytes) -> str:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    normalized = normalize_whitespace(text)
    if not normalized:
        raise DocumentParsingError("The uploaded text file was empty.")
    return normalized
