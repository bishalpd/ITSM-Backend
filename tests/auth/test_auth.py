import pytest


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "Test123456",
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "access_token" in data
    assert data["access_token"]


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "New Employee",
            "email": "newemployee@example.com",
            "password": "Test123456",
        },
    )
    assert response.status_code == 201, response.text


@pytest.mark.asyncio
async def test_register_duplicate_email(client, test_user):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "New Employee",
            "email": test_user.email,
            "password": "Test123456",
        },
    )
    assert response.status_code == 400, response.text
