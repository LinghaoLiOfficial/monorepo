from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.application.dto.storage import ObjectLoadResult
from app.application.ports.external_clients import ObjectStorageClient


@dataclass(slots=True)
class RunSaveObjectInput:
    file_path: Path
    file_data: bytes
    content_type: str | None = None


@dataclass(slots=True)
class RunLoadObjectInput:
    file_path: Path


class RunSaveObjectUseCase:
    def __init__(self, storage_client: ObjectStorageClient) -> None:
        self._storage_client = storage_client

    async def execute(self, payload: RunSaveObjectInput) -> None:
        await self._storage_client.save(
            file_path=payload.file_path,
            file_data=payload.file_data,
            content_type=payload.content_type,
        )


class RunLoadObjectUseCase:
    def __init__(self, storage_client: ObjectStorageClient) -> None:
        self._storage_client = storage_client

    async def execute(self, payload: RunLoadObjectInput) -> ObjectLoadResult:
        data, content_type = await self._storage_client.load(payload.file_path)
        return ObjectLoadResult(data=data, content_type=content_type)
