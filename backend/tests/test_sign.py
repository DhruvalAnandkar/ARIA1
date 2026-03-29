"""Tests for sign endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_speak_no_auth(client):
    """Speak endpoint requires authentication."""
    resp = await client.post("/sign/speak", json={"text": "Hello"})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_sos_no_auth(client):
    """SOS endpoint requires authentication."""
    resp = await client.post("/sign/sos", json={})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_transcript_no_auth(client):
    """Transcript endpoint requires authentication."""
    resp = await client.get("/sign/transcript?session_id=fake-id")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_speak_missing_text(client):
    """Speak endpoint should reject missing text field."""
    resp = await client.post(
        "/sign/speak",
        json={},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert resp.status_code in (401, 403, 422)
