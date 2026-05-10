from __future__ import annotations

from typing import Any

from app.core.error_codes import BusinessErrorCode, TechErrorCode


class DomainError(Exception):
    pass


class AppBusinessException(Exception):
    def __init__(
        self,
        error: BusinessErrorCode,
        *,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message or error.value.message)
        self.error = error
        self.message = message or error.value.message
        self.details = details or {}


class AppTechException(Exception):
    def __init__(
        self,
        error: TechErrorCode,
        *,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message or error.value.message)
        self.error = error
        self.message = message or error.value.message
        self.details = details or {}
