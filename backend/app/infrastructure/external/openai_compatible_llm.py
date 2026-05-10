from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from app.application.dto.llm import LLMTextResponse
from app.application.ports.external_clients import LLMClientPort


class OpenAICompatibleLLMClient(LLMClientPort):
    def __init__(self, *, base_url: str, api_key: str) -> None:
        self._client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    async def complete_text(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        response_format: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> LLMTextResponse:
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
        }
        if response_format is not None:
            kwargs["response_format"] = response_format
        if timeout_seconds is not None:
            kwargs["timeout"] = timeout_seconds

        completion = await self._client.chat.completions.create(**kwargs)
        content = completion.choices[0].message.content or ""
        return LLMTextResponse(content=content)
