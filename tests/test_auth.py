import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_signup(test_client: AsyncClient):
    user = {
        'email': 'some@gmail.com',
        'password': '123'
    }

    res = await test_client.post(f'/api/0.1.0/auth/signup', json=user)
    assert res.status_code == 201

    user = res.json()
    assert user['email'] == 'some@gmail.com'
