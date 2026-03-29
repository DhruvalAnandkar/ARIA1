"""Tests for auth endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_register_missing_fields(client):
    """Register should reject incomplete payloads."""
    resp = await client.post("/auth/register", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    """Register should reject invalid email format."""
    resp = await client.post("/auth/register", json={
        "email": "not-an-email",
        "password": "testpass123",
        "name": "Test",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_fields(client):
    """Login should reject incomplete payloads."""
    resp = await client.post("/auth/login", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_wrong_credentials(client):
    """Login should fail with non-existent user."""
    resp = await client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "wrong",
    })
    # Should be 401 or 400 depending on implementation
    assert resp.status_code in (400, 401)


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Health endpoint should be publicly accessible."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_protected_endpoint_no_token(client):
    """Protected endpoints should reject requests without auth."""
    resp = await client.get("/user/profile")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_protected_endpoint_bad_token(client):
    """Protected endpoints should reject invalid tokens."""
    resp = await client.get(
        "/user/profile",
        headers={"Authorization": "Bearer invalid-token-here"},
    )
    assert resp.status_code in (401, 403)
