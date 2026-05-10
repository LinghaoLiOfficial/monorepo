from __future__ import annotations

import asyncio
import mimetypes
from collections.abc import AsyncIterator, Callable, Generator
from functools import lru_cache
from pathlib import Path
from typing import Any, BinaryIO, ParamSpec, TypeVar, cast

import alibabacloud_oss_v2 as oss
import structlog

from app.application.ports.external_clients import ObjectStorageClient
from app.core.config import settings

logger = structlog.get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class ObjectStorageError(Exception):
    """Base error for object storage operations."""


class ObjectTooLargeError(ObjectStorageError):
    """Raised when loading file exceeds configured in-memory size limit."""


class AliyunOssStorage(ObjectStorageClient):
    def __init__(
        self,
        *,
        access_key_id: str,
        access_key_secret: str,
        bucket: str,
        region: str,
        endpoint: str,
        max_connections: int,
        disable_ssl: bool,
        use_cname: bool,
        load_max_size: int,
    ) -> None:
        self._client = self._build_client(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            region=region,
            endpoint=endpoint,
            max_connections=max_connections,
            disable_ssl=disable_ssl,
            use_cname=use_cname,
        )
        self._bucket = bucket
        self._load_max_size = load_max_size

    @staticmethod
    def _build_client(
        *,
        access_key_id: str,
        access_key_secret: str,
        region: str,
        endpoint: str,
        max_connections: int,
        disable_ssl: bool,
        use_cname: bool,
    ) -> oss.Client:
        cfg = oss.config.load_default()
        cfg.credentials_provider = oss.credentials.CredentialsProviderFunc(
            func=lambda: oss.credentials.Credentials(
                access_key_id=access_key_id,
                access_key_secret=access_key_secret,
            )
        )
        cfg.region = region
        cfg.disable_ssl = disable_ssl
        cfg.endpoint = endpoint
        cfg.use_cname = use_cname
        cfg.http_client = oss.transport.RequestsHttpClient(
            max_connections=max_connections
        )
        return oss.Client(cfg)

    async def save(
        self,
        file_path: Path,
        file_data: bytes,
        content_type: str | None = None,
    ) -> None:
        await self.save_stream(
            file_path=file_path,
            file_data=file_data,
            content_type=content_type,
        )

    async def save_stream(
        self,
        file_path: Path,
        file_data: bytes | BinaryIO,
        content_type: str | None = None,
    ) -> None:
        resolved_type = (
            content_type
            or mimetypes.guess_type(str(file_path))[0]
            or "application/octet-stream"
        )

        req = oss.PutObjectRequest(
            bucket=self._bucket,
            key=str(file_path),
            body=file_data,
            content_type=resolved_type,
        )
        await self._run_sync(self._client.put_object, req)
        logger.info(
            "oss_upload_succeeded", key=str(file_path), content_type=resolved_type
        )

    async def load(self, file_path: Path) -> tuple[bytes, str]:
        result: Any = await self._run_sync(
            self._client.get_object,
            oss.GetObjectRequest(bucket=self._bucket, key=str(file_path)),
        )

        content_type = result.headers.get("content-type", "application/octet-stream")
        content_length = int(result.headers.get("content-length", 0))
        if content_length > self._load_max_size:
            raise ObjectTooLargeError(
                f"Object size {content_length} exceeds limit {self._load_max_size}"
            )

        body_stream = cast(BinaryIO, result.body)
        try:
            file_data = await self._run_sync(body_stream.read)
        finally:
            await self._run_sync(body_stream.close)
        return file_data, content_type

    async def load_stream(
        self,
        file_path: Path,
        chunk_size: int = 1024 * 1024,
    ) -> tuple[AsyncIterator[bytes], str]:
        result: Any = await self._run_sync(
            self._client.get_object,
            oss.GetObjectRequest(bucket=self._bucket, key=str(file_path)),
        )
        content_type = result.headers.get("content-type", "application/octet-stream")
        body_stream = cast(BinaryIO, result.body)

        def iter_chunks() -> Generator[bytes, None, None]:
            try:
                while chunk := body_stream.read(chunk_size):
                    yield chunk
            finally:
                body_stream.close()

        async def async_iter() -> AsyncIterator[bytes]:
            iterator = iter_chunks()
            while True:
                chunk = await asyncio.to_thread(next, iterator, None)
                if chunk is None:
                    break
                yield chunk

        return async_iter(), content_type

    async def delete(self, file_path: Path) -> None:
        await self._run_sync(
            self._client.delete_object,
            oss.DeleteObjectRequest(bucket=self._bucket, key=str(file_path)),
        )
        logger.info("oss_delete_succeeded", key=str(file_path))

    async def exists(self, file_path: Path) -> bool:
        result = await self._run_sync(
            self._client.is_object_exist,
            bucket=self._bucket,
            key=str(file_path),
        )
        return bool(result)

    async def list_files(self, prefix: Path) -> list[str]:
        paginator = self._client.list_objects_v2_paginator()

        def collect() -> list[str]:
            files: list[str] = []
            for page in paginator.iter_page(
                oss.ListObjectsV2Request(bucket=self._bucket, prefix=str(prefix))
            ):
                for obj in page.contents:
                    files.append(obj.key)
            return files

        return await asyncio.to_thread(collect)

    async def _run_sync(
        self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> T:
        try:
            return await asyncio.to_thread(fn, *args, **kwargs)
        except Exception as exc:  # pragma: no cover - defensive wrapper
            logger.exception("oss_operation_failed", error=str(exc))
            raise ObjectStorageError(str(exc)) from exc


@lru_cache
def get_aliyun_oss_storage() -> AliyunOssStorage:
    if not settings.oss_enabled:
        raise RuntimeError("Aliyun OSS is disabled. Set OSS_ENABLED=true to enable it.")

    return AliyunOssStorage(
        access_key_id=settings.oss_access_key_id,
        access_key_secret=settings.oss_access_key_secret,
        bucket=settings.oss_bucket,
        region=settings.oss_region,
        endpoint=settings.oss_endpoint,
        max_connections=settings.oss_max_connections,
        disable_ssl=settings.oss_disable_ssl,
        use_cname=settings.oss_use_cname,
        load_max_size=settings.oss_load_max_size,
    )
