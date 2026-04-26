from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.schemas.common import ApiErrorResponse

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        logger.warning("app_exception", extra={"error_code": exc.error_code, "error_message": exc.message})
        payload = ApiErrorResponse(
            error_code=exc.error_code,
            error_message=exc.message,
            details=exc.details,
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump(mode="json"))

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("request_validation_error", extra={"errors": exc.errors()})
        payload = ApiErrorResponse(
            error_code="request_validation_error",
            error_message="The request payload is invalid.",
            details={"errors": exc.errors()},
        )
        return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))

    @app.exception_handler(FastAPIHTTPException)
    async def handle_http_exception(_: Request, exc: FastAPIHTTPException) -> JSONResponse:
        payload = ApiErrorResponse(
            error_code="http_error",
            error_message=str(exc.detail),
            details={"status_code": exc.status_code},
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump(mode="json"))

    @app.exception_handler(ResponseValidationError)
    async def handle_response_validation(_: Request, exc: ResponseValidationError) -> JSONResponse:
        logger.error("response_validation_error", extra={"errors": exc.errors()})
        payload = ApiErrorResponse(
            error_code="response_validation_error",
            error_message="The server generated an invalid response payload.",
            details={"errors": exc.errors()},
        )
        return JSONResponse(status_code=500, content=payload.model_dump(mode="json"))

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", exc_info=exc)
        payload = ApiErrorResponse(
            error_code="internal_server_error",
            error_message="An unexpected error occurred while processing the request.",
        )
        return JSONResponse(status_code=500, content=payload.model_dump(mode="json"))
