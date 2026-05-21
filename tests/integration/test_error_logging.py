"""
Integration tests: error logging behavior (4xx vs 5xx log levels).
Requires a live server at http://localhost:8000.
Run: pytest tests/integration/ -v -m integration
"""

import pytest
import requests

BASE_URL = "http://localhost:8000"
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module", autouse=True)
def require_server():
    """Skip all integration tests when the server is not reachable."""
    try:
        requests.get(f"{BASE_URL}/docs", timeout=2)
    except requests.exceptions.ConnectionError:
        pytest.skip("Live server not running at http://localhost:8000")


PLAYLIST_ID = "VLPLR48NTfP0M0OtpJgD2obWAuQF8yk0_F77"


def test_playlist_id_on_artist_endpoint_returns_400():
    """Passing a playlist ID to the artist endpoint should yield 400, not 500."""
    response = requests.get(
        f"{BASE_URL}/browse/artist/{PLAYLIST_ID}", timeout=30
    )
    assert response.status_code == 400, (
        f"Expected 400 for wrong ID type, got {response.status_code}"
    )


def test_playlist_id_on_user_endpoint_returns_400():
    """Passing a playlist ID to the user endpoint should yield 400, not 500."""
    response = requests.get(
        f"{BASE_URL}/browse/user/{PLAYLIST_ID}", timeout=30
    )
    assert response.status_code == 400, (
        f"Expected 400 for wrong ID type, got {response.status_code}"
    )


def test_invalid_filter_returns_4xx():
    """An invalid search filter should return 4xx (validation error)."""
    response = requests.get(
        f"{BASE_URL}/search", params={"query": "test", "filter": "invalid_filter"},
        timeout=30,
    )
    assert response.status_code in (400, 422), (
        f"Expected 400/422 for invalid filter, got {response.status_code}"
    )


def test_valid_search_returns_200():
    """A well-formed search request should return 200."""
    response = requests.get(
        f"{BASE_URL}/search", params={"query": "test", "limit": 1}, timeout=30
    )
    assert response.status_code == 200
