import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    response = await client.post(
        "/auth/signup",
        json={"email": "newuser@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data

@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient):
    payload = {"email": "duplicate@example.com", "password": "password123"}
    await client.post("/auth/signup", json=payload)
    
    response = await client.post("/auth/signup", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    email = "login@example.com"
    password = "correct_password"
    await client.post("/auth/signup", json={"email": email, "password": password})

    response = await client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):

    email = "badlogin@example.com"
    await client.post("/auth/signup", json={"email": email, "password": "correct_password"})

    response = await client.post(
        "/auth/login",
        json={"email": email, "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"