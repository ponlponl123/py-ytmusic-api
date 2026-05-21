"""
Integration tests: error handling scenarios.
Requires a live server at http://localhost:8000.
Run: pytest tests/integration/ -v -m integration
"""

import pytest
import httpx

BASE_URL = "http://localhost:8000"
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module", autouse=True)
def require_server():
    """Skip all integration tests when the server is not reachable."""
    try:
        import requests  # pylint: disable=import-outside-toplevel
        requests.get(f"{BASE_URL}/docs", timeout=2)
    except Exception:  # pylint: disable=broad-exception-caught
        pytest.skip("Live server not running at http://localhost:8000")


@pytest.mark.anyio
async def test_health_endpoint():
    """Health endpoint should return 200."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/search/health")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_search_with_valid_query():
    """A valid search should return 200."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/search/", params={"query": "nightcore", "limit": 5}
        )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_invalid_video_id_does_not_crash():
    """An invalid video ID should return a handled error (not 500)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/browse/song/invalid_id")
    assert response.status_code != 500


@pytest.mark.anyio
async def test_api_status_endpoint():
    """Global API status endpoint should return a structured response."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
