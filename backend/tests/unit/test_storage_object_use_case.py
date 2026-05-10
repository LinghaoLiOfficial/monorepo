from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from app.application.use_cases.storage_object import (
    RunLoadObjectInput,
    RunLoadObjectUseCase,
    RunSaveObjectInput,
    RunSaveObjectUseCase,
)


class _FakeStorageClient:
    def __init__(self) -> None:
        self.saved: dict[str, tuple[bytes, str | None]] = {}

    async def save(
        self,
        file_path: Path,
        file_data: bytes,
        content_type: str | None = None,
    ) -> None:
        self.saved[str(file_path)] = (file_data, content_type)

    async def load(self, file_path: Path) -> tuple[bytes, str]:
        file_data, content_type = self.saved[str(file_path)]
        return file_data, content_type or "application/octet-stream"

    async def load_stream(
        self,
        file_path: Path,
        chunk_size: int = 1024 * 1024,
    ) -> tuple[AsyncIterator[bytes], str]:
        raise NotImplementedError

    async def delete(self, file_path: Path) -> None:
        self.saved.pop(str(file_path), None)

    async def exists(self, file_path: Path) -> bool:
        return str(file_path) in self.saved

    async def list_files(self, prefix: Path) -> list[str]:
        prefix_str = str(prefix)
        return [k for k in self.saved if k.startswith(prefix_str)]


@pytest.mark.asyncio
async def test_save_object_use_case_success() -> None:
    storage = _FakeStorageClient()
    use_case = RunSaveObjectUseCase(storage_client=storage)

    await use_case.execute(
        RunSaveObjectInput(
            file_path=Path("uploads/a.txt"),
            file_data=b"hello",
            content_type="text/plain",
        )
    )

    assert await storage.exists(Path("uploads/a.txt"))


@pytest.mark.asyncio
async def test_load_object_use_case_success() -> None:
    storage = _FakeStorageClient()
    await storage.save(Path("uploads/b.txt"), b"world", "text/plain")

    use_case = RunLoadObjectUseCase(storage_client=storage)
    result = await use_case.execute(RunLoadObjectInput(file_path=Path("uploads/b.txt")))

    assert result.data == b"world"
    assert result.content_type == "text/plain"
