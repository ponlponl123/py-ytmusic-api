"""
Unit tests for newly added ytmusicapi routes and features.
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest

from src.main import app
from src.utils.client import YTMusicClient


@pytest.fixture(autouse=True)
def reset_client_cache():
    YTMusicClient.reset_client()
    yield
    YTMusicClient.reset_client()


def test_explore_main_route(monkeypatch):
    mock_ytmusic = MagicMock()
    mock_ytmusic.get_explore.return_value = {"categories": ["New Releases"]}
    monkeypatch.setattr(YTMusicClient, "get_client", MagicMock(return_value=mock_ytmusic))

    client = TestClient(app)
    res = client.get("/explore/explore")
    assert res.status_code == 200
    assert res.json()["result"]["categories"] == ["New Releases"]



def test_credits_route(monkeypatch):
    mock_ytmusic = MagicMock()
    mock_ytmusic.get_song_credits.return_value = {"performers": ["Test Artist"]}
    monkeypatch.setattr(YTMusicClient, "get_client", MagicMock(return_value=mock_ytmusic))

    client = TestClient(app)
    res = client.get("/browse/credits/MPREb_test")
    assert res.status_code == 200
    assert res.json()["result"]["performers"] == ["Test Artist"]


def test_join_collaborative_playlist_route(monkeypatch):
    mock_ytmusic = MagicMock()
    mock_ytmusic.join_collaborative_playlist.return_value = {"status": "SUCCESS"}
    monkeypatch.setattr(YTMusicClient, "get_client", MagicMock(return_value=mock_ytmusic))

    client = TestClient(app)
    res = client.post(
        "/playlists/join_collaborative",
        params={"playlistId": "PL123", "joinCollaborationToken": "token_abc"},
    )
    assert res.status_code == 200
    assert res.json()["result"]["status"] == "SUCCESS"


def test_signature_timestamp_route(monkeypatch):
    mock_ytmusic = MagicMock()
    mock_ytmusic.get_signatureTimestamp.return_value = 19800
    monkeypatch.setattr(YTMusicClient, "get_client", MagicMock(return_value=mock_ytmusic))

    client = TestClient(app)
    res = client.get("/watch/signature_timestamp")
    assert res.status_code == 200
    assert res.json()["result"] == 19800


def test_explore_charts_route(monkeypatch):
    mock_ytmusic = MagicMock()
    mock_ytmusic.get_charts.return_value = {"countries": ["US", "JP"]}
    monkeypatch.setattr(YTMusicClient, "get_client", MagicMock(return_value=mock_ytmusic))

    client = TestClient(app)
    res = client.get("/explore/charts/US")
    assert res.status_code == 200
    assert res.json()["result"]["countries"] == ["US", "JP"]

