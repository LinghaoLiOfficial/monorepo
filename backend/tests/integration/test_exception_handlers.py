import pytest
from fastapi import APIRouter
from httpx import AsyncClient

from app.core.error_codes import BusinessErrorCode, TechErrorCode
from app.core.exceptions import AppBusinessException, AppTechException
from app.main import app

router = APIRouter()


@router.get("/test/business")
async def raise_business() -> None:
    raise AppBusinessException(
        BusinessErrorCode.NOT_FOUND,
        message="User not found",
        details={"user_id": "u-1"},
    )


@router.get("/test/tech")
async def raise_tech() -> None:
    raise AppTechException(
        TechErrorCode.SERVICE_UNAVAILABLE,
        message="Dependency down",
        details={"service": "third-party"},
    )


@router.get("/test/unhandled")
async def raise_unhandled() -> None:
    raise RuntimeError("boom")


@router.get("/test/validation")
async def raise_validation(age: int) -> dict[str, int]:
    return {"age": age}


app.include_router(router)


@pytest.mark.asyncio
async def test_business_exception_response(client: AsyncClient) -> None:
    response = await client.get(
        "/test/business", headers={"x-request-id": "rid-business"}
    )

    assert response.status_code == 404
    payload = response.json()
    assert payload["code"] == "NOT_FOUND"
    assert payload["message"] == "User not found"
    assert payload["details"] == {"user_id": "u-1"}
    assert payload["request_id"] == "rid-business"


@pytest.mark.asyncio
async def test_tech_exception_response(client: AsyncClient) -> None:
    response = await client.get("/test/tech", headers={"x-request-id": "rid-tech"})

    assert response.status_code == 503
    payload = response.json()
    assert payload["code"] == "SERVICE_UNAVAILABLE"
    assert payload["message"] == "Dependency down"
    assert payload["details"] == {"service": "third-party"}
    assert payload["request_id"] == "rid-tech"


@pytest.mark.asyncio
async def test_unhandled_exception_response(client: AsyncClient) -> None:
    response = await client.get(
        "/test/unhandled", headers={"x-request-id": "rid-unhandled"}
    )

    assert response.status_code == 500
    payload = response.json()
    assert payload["code"] == "INTERNAL_SERVER_ERROR"
    assert payload["message"] == "Internal server error"
    assert payload["details"] == {}
    assert payload["request_id"] == "rid-unhandled"


@pytest.mark.asyncio
async def test_validation_exception_response(client: AsyncClient) -> None:
    response = await client.get(
        "/test/validation",
        params={"age": "not-int"},
        headers={"x-request-id": "rid-validation"},
    )

    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == "BAD_REQUEST"
    assert payload["message"] == "Bad request"
    assert "errors" in payload["details"]
    assert payload["request_id"] == "rid-validation"
