from collections.abc import AsyncIterator
from pathlib import Path
from typing import Protocol

from app.application.dto.llm import LLMTextResponse


class ExternalClient(Protocol):
    pass


class ObjectStorageClient(Protocol):
    async def save(
        self,
        file_path: Path,
        file_data: bytes,
        content_type: str | None = None,
    ) -> None: ...

    async def load(self, file_path: Path) -> tuple[bytes, str]: ...

    async def load_stream(
        self,
        file_path: Path,
        chunk_size: int = 1024 * 1024,
    ) -> tuple[AsyncIterator[bytes], str]: ...

    async def delete(self, file_path: Path) -> None: ...

    async def exists(self, file_path: Path) -> bool: ...

    async def list_files(self, prefix: Path) -> list[str]: ...


class LLMClientPort(Protocol):
    async def complete_text(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        response_format: dict[str, str] | None = None,
        timeout_seconds: float | None = None,
    ) -> LLMTextResponse: ...
