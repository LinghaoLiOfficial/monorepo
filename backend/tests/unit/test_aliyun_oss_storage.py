from pathlib import Path
from typing import Any

import pytest

from app.infrastructure.storage.aliyun_oss import (
    AliyunOssStorage,
    ObjectTooLargeError,
)


class _FakeBody:
    def __init__(self, data: bytes) -> None:
        self._data = data
        self._offset = 0

    def read(self, size: int = -1) -> bytes:
        if size == -1:
            size = len(self._data) - self._offset
        chunk = self._data[self._offset : self._offset + size]
        self._offset += len(chunk)
        return chunk

    def close(self) -> None:
        return None


class _FakeResponse:
    def __init__(self, data: bytes, content_type: str = "text/plain") -> None:
        self.headers = {
            "content-type": content_type,
            "content-length": str(len(data)),
        }
        self.body = _FakeBody(data)


class _FakeClient:
    def __init__(self, data: bytes = b"hello") -> None:
        self.data = data

    def put_object(self, _req: Any) -> None:
        return None

    def get_object(self, _req: Any) -> _FakeResponse:
        return _FakeResponse(self.data)

    def delete_object(self, _req: Any) -> None:
        return None

    def is_object_exist(self, **_kwargs: Any) -> bool:
        return True


@pytest.mark.asyncio
async def test_load_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        AliyunOssStorage,
        "_build_client",
        staticmethod(lambda **_kwargs: _FakeClient(b"abc")),
    )
    storage = AliyunOssStorage(
        access_key_id="id",
        access_key_secret="sec",
        bucket="b",
        region="cn-hangzhou",
        endpoint="oss-cn-hangzhou.aliyuncs.com",
        max_connections=10,
        disable_ssl=False,
        use_cname=False,
        load_max_size=10,
    )

    data, content_type = await storage.load(Path("a.txt"))

    assert data == b"abc"
    assert content_type == "text/plain"


@pytest.mark.asyncio
async def test_load_too_large(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        AliyunOssStorage,
        "_build_client",
        staticmethod(lambda **_kwargs: _FakeClient(b"abcdef")),
    )
    storage = AliyunOssStorage(
        access_key_id="id",
        access_key_secret="sec",
        bucket="b",
        region="cn-hangzhou",
        endpoint="oss-cn-hangzhou.aliyuncs.com",
        max_connections=10,
        disable_ssl=False,
        use_cname=False,
        load_max_size=3,
    )

    with pytest.raises(ObjectTooLargeError):
        await storage.load(Path("a.txt"))
