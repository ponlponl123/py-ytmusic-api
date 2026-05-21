"""
Unit test: browse /song_related endpoint using in-process TestClient.
No live server required.
"""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

TEST_SONGS = [
    "MPTRt_J06gtxzw8Sv",  # Standard song browse ID
    "b3rFbkFjRrA",        # Plain video ID (previously problematic)
]


def test_song_related_responds():
    """Both song IDs should return a non-500 response from the endpoint."""
    for song_id in TEST_SONGS:
        response = client.get(f"/browse/song_related/{song_id}")
        # We expect either a successful result or a handled error (not an unhandled crash)
        assert response.status_code != 500, (
            f"Unexpected server error for song_id={song_id}: {response.json()}"
        )


def test_song_related_structure_on_success():
    """When a 200 is returned, check the response has expected fields."""
    for song_id in TEST_SONGS:
        response = client.get(f"/browse/song_related/{song_id}")
        if response.status_code == 200:
            data = response.json()
            assert "related_browse_id" in data or "related_content" in data, (
                f"Unexpected 200 response shape for {song_id}: {data}"
            )
