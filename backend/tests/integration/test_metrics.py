import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_metrics(client: AsyncClient) -> None:
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
