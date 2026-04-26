class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 400,
        error_code: str = "app_error",
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class ResourceNotFoundError(AppException):
    """Raised when a requested resource cannot be found."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=404, error_code="not_found")


class DocumentParsingError(AppException):
    """Raised when document parsing fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=400, error_code="document_parsing_error")


class LLMOutputError(AppException):
    """Raised when an LLM response is invalid or unusable."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=502, error_code="llm_output_error")


class WorkflowStateError(AppException):
    """Raised when the workflow step is invalid for the current state."""

    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=409, error_code="workflow_state_error")
