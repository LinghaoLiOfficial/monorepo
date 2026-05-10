from pathlib import Path
from typing import Any

import pytest

from app.application.dto.llm import LLMTextResponse
from app.application.services.llm_prompt_service import (
    LLMJsonParseError,
    LLMPromptService,
    LLMSchemaValidationError,
    LLMTemplateFormatError,
)


class _FakeLLMClient:
    def __init__(self, content: str) -> None:
        self._content = content

    async def complete_text(self, **_kwargs: Any) -> LLMTextResponse:
        return LLMTextResponse(content=self._content)


def _fixture(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / "llm" / name


def test_render_messages_success() -> None:
    messages = LLMPromptService.render_messages(
        template_path=_fixture("tech_create_template.j2"),
        params={"en_name": "Natural Language Processing"},
    )

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "Natural Language Processing" in messages[1]["content"]


def test_render_messages_invalid_template(tmp_path: Path) -> None:
    bad_template = tmp_path / "bad.j2"
    bad_template.write_text("hello", encoding="utf-8")

    with pytest.raises(LLMTemplateFormatError):
        LLMPromptService.render_messages(template_path=bad_template, params={})


def test_parse_json_output_code_block() -> None:
    payload = """```json
    {"a": "b"}
    ```"""
    parsed = LLMPromptService.parse_json_output(payload)
    assert parsed == {"a": "b"}


def test_parse_json_output_invalid() -> None:
    with pytest.raises(LLMJsonParseError):
        LLMPromptService.parse_json_output("not-json")


def test_validate_schema_fail() -> None:
    schema = {
        "type": "object",
        "required": ["x"],
        "properties": {"x": {"type": "string"}},
    }
    with pytest.raises(LLMSchemaValidationError):
        LLMPromptService.validate_schema(data={"y": "z"}, schema=schema)


@pytest.mark.asyncio
async def test_run_template_json_success() -> None:
    content = (
        '{"chinese_name":"自然语言处理","core_function":"analyze language",'
        '"research_application":"used in NLP research"}'
    )
    service = LLMPromptService(llm_client=_FakeLLMClient(content=content))

    result = await service.run_template_json(
        model="dummy-model",
        template_path=_fixture("tech_create_template.j2"),
        input_params={"en_name": "Natural Language Processing"},
        schema_path=_fixture("tech_create_schema.json"),
    )

    assert result.data["chinese_name"] == "自然语言处理"
