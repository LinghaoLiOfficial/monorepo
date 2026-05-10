from __future__ import annotations

from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.core.error_codes import BusinessErrorCode, TechErrorCode
from app.core.exceptions import AppBusinessException, AppTechException

logger = structlog.get_logger(__name__)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "")


def _error_payload(
    *,
    code: str,
    message: str,
    details: dict[str, Any],
    request_id: str,
) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "details": details,
        "request_id": request_id,
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppBusinessException)
    async def on_business_exception(
        request: Request,
        exc: AppBusinessException,
    ) -> JSONResponse:
        logger.warning(
            "business_exception",
            path=request.url.path,
            code=exc.error.value.code,
            request_id=_request_id(request),
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.error.value.http_status,
            content=_error_payload(
                code=exc.error.value.code,
                message=exc.message,
                details=exc.details,
                request_id=_request_id(request),
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def on_validation_exception(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(
            "request_validation_exception",
            path=request.url.path,
            request_id=_request_id(request),
            details=exc.errors(),
        )
        bad_request = BusinessErrorCode.BAD_REQUEST
        return JSONResponse(
            status_code=bad_request.value.http_status,
            content=_error_payload(
                code=bad_request.value.code,
                message=bad_request.value.message,
                details={"errors": exc.errors()},
                request_id=_request_id(request),
            ),
        )

    @app.exception_handler(AppTechException)
    async def on_tech_exception(
        request: Request,
        exc: AppTechException,
    ) -> JSONResponse:
        logger.error(
            "tech_exception",
            path=request.url.path,
            code=exc.error.value.code,
            request_id=_request_id(request),
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.error.value.http_status,
            content=_error_payload(
                code=exc.error.value.code,
                message=exc.message,
                details=exc.details,
                request_id=_request_id(request),
            ),
        )

    @app.exception_handler(Exception)
    async def on_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
        internal_error = TechErrorCode.INTERNAL_SERVER_ERROR
        logger.exception(
            "unhandled_exception",
            path=request.url.path,
            request_id=_request_id(request),
            error=str(exc),
        )
        return JSONResponse(
            status_code=internal_error.value.http_status,
            content=_error_payload(
                code=internal_error.value.code,
                message=internal_error.value.message,
                details={},
                request_id=_request_id(request),
            ),
        )
