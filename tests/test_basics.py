import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_root(test_client: AsyncClient):
    response = await test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello World"