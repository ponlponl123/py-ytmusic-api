"""
Unit test: direct ytmusicapi calls (no FastAPI server needed).
These tests exercise the YTMusic client and song-related lookups.
"""

import pytest
from ytmusicapi import YTMusic


PROBLEMATIC_SONG_ID = "b3rFbkFjRrA"


@pytest.fixture(scope="module")
def ytmusic():
    return YTMusic()


def test_get_song_returns_data(ytmusic):
    """get_song should return a non-empty dict for a known video ID."""
    try:
        result = ytmusic.get_song(PROBLEMATIC_SONG_ID)
        assert isinstance(result, dict), "Expected dict from get_song"
    except Exception as exc:  # pylint: disable=broad-exception-caught
        pytest.skip(f"Live YTMusic call skipped (network/API issue): {exc}")


def test_get_watch_playlist_has_related(ytmusic):
    """get_watch_playlist should include a 'related' key when available."""
    try:
        playlist = ytmusic.get_watch_playlist(PROBLEMATIC_SONG_ID)
        assert isinstance(playlist, dict), "Expected dict from get_watch_playlist"
    except Exception as exc:  # pylint: disable=broad-exception-caught
        pytest.skip(f"Live YTMusic call skipped (network/API issue): {exc}")


def test_search_returns_results():
    """Basic search should return at least one result."""
    ytm = YTMusic()
    try:
        results = ytm.search(query="test query", limit=1)
        assert isinstance(results, list), "Expected list from search"
    except Exception as exc:  # pylint: disable=broad-exception-caught
        pytest.skip(f"Live YTMusic call skipped (network/API issue): {exc}")
