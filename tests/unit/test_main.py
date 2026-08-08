"""
Unit tests for the FastAPI root and status endpoints.
Uses an in-process TestClient — no live server required.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.anyio
async def test_root_returns_200():
    """Root endpoint should return HTTP 200 with a healthy status payload."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.anyio
async def test_docs_endpoint_returns_200():
    """Custom Swagger UI endpoint should be reachable."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/docs")

    assert response.status_code == 200


@pytest.mark.anyio
async def test_api_status_endpoint_returns_200():
    """
    Global API status endpoint should return a structured response.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/status")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "ytmusicapi_version" in data
    assert data["timestamp"] != "2025-11-02T16:51:27Z"
