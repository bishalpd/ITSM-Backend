import pytest


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()
