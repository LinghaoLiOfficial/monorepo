from typing import Any

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: dict[str, Any] = Field(default_factory=dict)
