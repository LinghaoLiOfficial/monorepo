from pathlib import Path
from typing import Any

import pytest

from app.application.dto.llm import LLMTextResponse
from app.application.services.llm_prompt_service import LLMPromptService
from app.application.use_cases.llm_template_json import (
    RunLLMTemplateJsonInput,
    RunLLMTemplateJsonUseCase,
)


class _FakeLLMClient:
    def __init__(self, content: str) -> None:
        self._content = content

    async def complete_text(self, **_kwargs: Any) -> LLMTextResponse:
        return LLMTextResponse(content=self._content)


def _fixture(name: str) -> Path:
    return Path(__file__).parent / "fixtures" / "llm" / name


@pytest.mark.asyncio
async def test_use_case_execute_success() -> None:
    content = (
        '{"chinese_name":"自然语言处理","core_function":"analyze language",'
        '"research_application":"used in NLP research"}'
    )
    prompt_service = LLMPromptService(llm_client=_FakeLLMClient(content=content))
    use_case = RunLLMTemplateJsonUseCase(prompt_service=prompt_service)

    payload = RunLLMTemplateJsonInput(
        model="dummy-model",
        template_path=_fixture("tech_create_template.j2"),
        schema_path=_fixture("tech_create_schema.json"),
        input_params={"en_name": "Natural Language Processing"},
    )

    result = await use_case.execute(payload)

    assert result.data["core_function"] == "analyze language"
