from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.application.dto.llm import LLMPromptResult
from app.application.services.llm_prompt_service import LLMPromptService


@dataclass(slots=True)
class RunLLMTemplateJsonInput:
    model: str
    template_path: Path
    schema_path: Path
    input_params: dict[str, Any]
    timeout_seconds: float | None = None
    max_attempts: int = 2


class RunLLMTemplateJsonUseCase:
    def __init__(self, prompt_service: LLMPromptService) -> None:
        self._prompt_service = prompt_service

    async def execute(self, payload: RunLLMTemplateJsonInput) -> LLMPromptResult:
        return await self._prompt_service.run_template_json(
            model=payload.model,
            template_path=payload.template_path,
            input_params=payload.input_params,
            schema_path=payload.schema_path,
            timeout_seconds=payload.timeout_seconds,
            max_attempts=payload.max_attempts,
        )
