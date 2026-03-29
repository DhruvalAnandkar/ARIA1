"""Tests for guide endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_obstacle_no_auth(client):
    """Obstacle endpoint requires authentication."""
    resp = await client.post("/guide/obstacle", json={"frame": "base64data"})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_navigate_no_auth(client):
    """Navigate endpoint requires authentication."""
    resp = await client.post("/guide/navigate", json={
        "lat": 41.1499,
        "lng": -81.3415,
        "destination": "Kent State Library",
    })
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_obstacle_missing_frame(client):
    """Obstacle endpoint should reject missing frame field."""
    resp = await client.post(
        "/guide/obstacle",
        json={},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code in (401, 403, 422)


@pytest.mark.asyncio
async def test_navigate_missing_fields(client):
    """Navigate endpoint should reject incomplete payload."""
    resp = await client.post(
        "/guide/navigate",
        json={"lat": 41.15},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code in (401, 403, 422)


@pytest.mark.asyncio
async def test_speak_no_auth(client):
    """Guide speak endpoint requires authentication."""
    resp = await client.post("/guide/speak", json={"text": "Turn left"})
    assert resp.status_code in (401, 403)
