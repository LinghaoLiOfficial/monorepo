from dataclasses import dataclass
from enum import Enum

from fastapi import status


@dataclass(frozen=True, slots=True)
class ErrorDescriptor:
    code: str
    message: str
    http_status: int


class BusinessErrorCode(Enum):
    BAD_REQUEST = ErrorDescriptor(
        "BAD_REQUEST", "Bad request", status.HTTP_400_BAD_REQUEST
    )
    UNAUTHORIZED = ErrorDescriptor(
        "UNAUTHORIZED", "Unauthorized", status.HTTP_401_UNAUTHORIZED
    )
    FORBIDDEN = ErrorDescriptor("FORBIDDEN", "Forbidden", status.HTTP_403_FORBIDDEN)
    NOT_FOUND = ErrorDescriptor(
        "NOT_FOUND", "Resource not found", status.HTTP_404_NOT_FOUND
    )
    CONFLICT = ErrorDescriptor(
        "CONFLICT", "Resource conflict", status.HTTP_409_CONFLICT
    )
    PAYLOAD_TOO_LARGE = ErrorDescriptor(
        "PAYLOAD_TOO_LARGE",
        "Payload too large",
        status.HTTP_413_CONTENT_TOO_LARGE,
    )


class TechErrorCode(Enum):
    INTERNAL_SERVER_ERROR = ErrorDescriptor(
        "INTERNAL_SERVER_ERROR",
        "Internal server error",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
    SERVICE_UNAVAILABLE = ErrorDescriptor(
        "SERVICE_UNAVAILABLE",
        "Service unavailable",
        status.HTTP_503_SERVICE_UNAVAILABLE,
    )
