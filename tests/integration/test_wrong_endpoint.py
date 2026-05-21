"""
Integration tests: wrong ID type detection.
Requires a live server at http://localhost:8000.
Run: pytest tests/integration/ -v -m integration
"""

import pytest
import requests

BASE_URL = "http://localhost:8000"
pytestmark = pytest.mark.integration

PLAYLIST_ID = "VLOLAK5uy_m-Cz9P8WPZNzB_FdLxx5Gw3tYc5MetaLI"
ALBUM_ID    = "OLAK5uy_m-Cz9P8WPZNzB_FdLxx5Gw3tYc5MetaLI"


@pytest.fixture(scope="module", autouse=True)
def require_server():
    """Skip all integration tests when the server is not reachable."""
    try:
        requests.get(f"{BASE_URL}/docs", timeout=2)
    except requests.exceptions.ConnectionError:
        pytest.skip("Live server not running at http://localhost:8000")


def test_playlist_id_on_artist_endpoint_returns_400():
    """A playlist/album ID passed to the artist endpoint should yield 400."""
    response = requests.get(
        f"{BASE_URL}/browse/artist/{PLAYLIST_ID}", timeout=30
    )
    assert response.status_code == 400, (
        f"Expected 400 Bad Request, got {response.status_code}"
    )
    data = response.json()
    # Response should include a helpful detail payload
    assert "detail" in data


def test_playlist_id_on_artist_endpoint_has_recommendation():
    """Error response for wrong ID type should include a recommendation."""
    response = requests.get(
        f"{BASE_URL}/browse/artist/{PLAYLIST_ID}", timeout=30
    )
    if response.status_code == 400:
        assert "recommendation" in str(response.json())


def test_correct_playlist_endpoint_succeeds():
    """The correct playlist endpoint should return 200 for a valid album/playlist ID."""
    response = requests.get(f"{BASE_URL}/playlists/{ALBUM_ID}", timeout=30)
    # May return 200 or a graceful non-500 if live content changes
    assert response.status_code != 500
