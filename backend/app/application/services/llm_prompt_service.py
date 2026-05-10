from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path
from typing import Any, cast

import structlog
from jinja2 import Template
from jsonschema import Draft202012Validator, ValidationError

from app.application.dto.llm import LLMPromptResult
from app.application.ports.external_clients import LLMClientPort

logger = structlog.get_logger(__name__)

_JSON_BLOCK_PATTERN = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)


class LLMPromptServiceError(Exception):
    """Base error for LLM prompt service."""


class LLMTemplateFormatError(LLMPromptServiceError):
    """Raised when template does not match expected message sections."""


class LLMJsonParseError(LLMPromptServiceError):
    """Raised when LLM output cannot be parsed as JSON."""


class LLMSchemaValidationError(LLMPromptServiceError):
    """Raised when parsed JSON fails schema validation."""


class LLMPromptService:
    def __init__(self, llm_client: LLMClientPort) -> None:
        self._llm_client = llm_client

    async def run_template_json(
        self,
        *,
        model: str,
        template_path: Path,
        input_params: dict[str, Any],
        schema_path: Path,
        timeout_seconds: float | None = None,
        max_attempts: int = 2,
    ) -> LLMPromptResult:
        messages = self.render_messages(
            template_path=template_path, params=input_params
        )
        schema = self.load_schema(schema_path)

        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            try:
                output = await self._llm_client.complete_text(
                    model=model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    timeout_seconds=timeout_seconds,
                )
                parsed = self.parse_json_output(output.content)
                self.validate_schema(parsed, schema)
                return LLMPromptResult(data=parsed)
            except (LLMJsonParseError, LLMSchemaValidationError) as exc:
                last_error = exc
                logger.warning(
                    "llm_prompt_validation_retry",
                    attempt=attempt,
                    max_attempts=max_attempts,
                    error=str(exc),
                    model=model,
                )
                if attempt < max_attempts:
                    await asyncio.sleep(0)
                    continue
                raise

        raise LLMPromptServiceError(
            "Unhandled LLM prompt service state"
        ) from last_error

    @staticmethod
    def render_messages(
        *,
        template_path: Path,
        params: dict[str, Any],
    ) -> list[dict[str, str]]:
        template_content = template_path.read_text(encoding="utf-8")
        rendered = Template(template_content).render(**params)

        if "===SYSTEM===" not in rendered or "===USER===" not in rendered:
            raise LLMTemplateFormatError(
                "Template must contain ===SYSTEM=== and ===USER=== delimiters"
            )

        system_raw, user_raw = rendered.split("===USER===", maxsplit=1)
        system_text = system_raw.replace("===SYSTEM===", "", 1).strip()
        user_text = user_raw.strip()

        if not system_text or not user_text:
            raise LLMTemplateFormatError(
                "System and user prompt parts must be non-empty"
            )

        return [
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_text},
        ]

    @staticmethod
    def load_schema(schema_path: Path) -> dict[str, Any]:
        payload = json.loads(schema_path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            if not payload:
                raise LLMSchemaValidationError("Schema list must not be empty")
            item = payload[0]
            if not isinstance(item, dict):
                raise LLMSchemaValidationError(
                    "Schema list first item must be an object"
                )
            return cast(dict[str, Any], item)
        if not isinstance(payload, dict):
            raise LLMSchemaValidationError(
                "Schema file must contain a JSON object or list"
            )
        return cast(dict[str, Any], payload)

    @staticmethod
    def parse_json_output(raw_text: str) -> dict[str, Any]:
        candidate = raw_text.strip()

        match = _JSON_BLOCK_PATTERN.search(candidate)
        if match:
            candidate = match.group(1).strip()

        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise LLMJsonParseError(f"Invalid JSON output: {exc}") from exc

        if not isinstance(parsed, dict):
            raise LLMJsonParseError("JSON output must be an object")

        return cast(dict[str, Any], parsed)

    @staticmethod
    def validate_schema(data: dict[str, Any], schema: dict[str, Any]) -> None:
        validator = Draft202012Validator(schema=schema)
        errors: list[ValidationError] = sorted(
            validator.iter_errors(data), key=lambda e: e.path
        )
        if errors:
            first = errors[0]
            raise LLMSchemaValidationError(first.message)
