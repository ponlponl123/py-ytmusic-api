"""
Integration tests: user & artist endpoint cross-fallback behavior.
Requires a live server at http://localhost:8000.
Run: pytest tests/integration/ -v -m integration
"""

import pytest
import requests

BASE_URL = "http://localhost:8000"
pytestmark = pytest.mark.integration

CHANNELS = [
    ("UCZwlNfizEaM-kqPTAQ2ptVg", "Kobo Kanaeru"),
    ("UCz4jhqrCfthF8NnldZeK_rw", "Generic Channel"),
]


@pytest.fixture(scope="module", autouse=True)
def require_server():
    """Skip all integration tests when the server is not reachable."""
    try:
        requests.get(f"{BASE_URL}/docs", timeout=2)
    except requests.exceptions.ConnectionError:
        pytest.skip("Live server not running at http://localhost:8000")


@pytest.mark.parametrize("channel_id,name", CHANNELS)
def test_user_endpoint_does_not_crash(channel_id, name):
    """User endpoint should return 200 or a handled error — never 500."""
    response = requests.get(
        f"{BASE_URL}/browse/user/{channel_id}", timeout=30
    )
    assert response.status_code != 500, (
        f"Server error for {name} ({channel_id}): {response.json()}"
    )


@pytest.mark.parametrize("channel_id,name", CHANNELS)
def test_artist_endpoint_does_not_crash(channel_id, name):
    """Artist endpoint should return 200 or a handled error — never 500."""
    response = requests.get(
        f"{BASE_URL}/browse/artist/{channel_id}", timeout=30
    )
    assert response.status_code != 500, (
        f"Server error for {name} ({channel_id}): {response.json()}"
    )


def test_user_200_has_result_key():
    """When user endpoint returns 200, the body should include 'result'."""
    channel_id, _ = CHANNELS[0]
    response = requests.get(f"{BASE_URL}/browse/user/{channel_id}", timeout=30)
    if response.status_code == 200:
        assert "result" in response.json()
