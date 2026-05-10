from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class LLMTextResponse:
    content: str


@dataclass(slots=True)
class LLMPromptResult:
    data: dict[str, Any]
