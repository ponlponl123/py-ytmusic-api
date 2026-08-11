"""
Unit tests for per-user cookie and auth support in YTMusicClient.
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


def test_get_client_default():
    client1 = YTMusicClient.get_client()
    client2 = YTMusicClient.get_client(None)
    client3 = YTMusicClient.get_client("")
    assert client1 is client2
    assert client2 is client3


def test_get_client_with_custom_cookie(monkeypatch):
    mock_ytmusic_cls = MagicMock()
    monkeypatch.setattr("src.utils.client.YTMusic", mock_ytmusic_cls)

    cookie_str = "VISITOR_INFO1_LIVE=test_visitor; __Secure-3PAPISID=test_sapisid"
    client_a = YTMusicClient.get_client(cookie_str)
    client_b = YTMusicClient.get_client(cookie_str)

    # Identical cookie should return cached instance
    assert client_a is client_b
    assert mock_ytmusic_cls.call_count == 1


def test_get_client_from_request_headers(monkeypatch):
    mock_client = MagicMock()
    mock_get_client = MagicMock(return_value=mock_client)
    monkeypatch.setattr(YTMusicClient, "get_client", mock_get_client)

    # Test 1: x-ytmusic-cookie header with metadata
    req_custom = MagicMock()
    req_custom.headers = {
        "x-ytmusic-cookie": "custom_cookie_val",
        "accept-language": "th-TH,th;q=0.9",
        "user-agent": "Mozilla/5.0 TestAgent",
        "x-forwarded-for": "203.0.113.1, 10.0.0.1",
        "x-user-country": "TH",
        "x-user-timezone": "Asia/Bangkok",
    }
    req_custom.query_params = {}
    req_custom.client = MagicMock(host="10.0.0.1")
    YTMusicClient.get_client_from_request(req_custom)
    mock_get_client.assert_called_with(
        cookie_or_auth="custom_cookie_val",
        language="th-TH,th;q=0.9",
        user_agent="Mozilla/5.0 TestAgent",
        user_ip="203.0.113.1",
        user_country="TH",
        user_timezone="Asia/Bangkok",
        sec_ch_ua=None,
        sec_ch_ua_mobile=None,
        sec_ch_ua_platform=None,
    )

    # Test 2: standard cookie header
    req_standard = MagicMock()
    req_standard.headers = {"cookie": "standard_cookie_val"}
    req_standard.query_params = {}
    req_standard.client = None
    YTMusicClient.get_client_from_request(req_standard)
    mock_get_client.assert_called_with(
        cookie_or_auth="standard_cookie_val",
        language=None,
        user_agent=None,
        user_ip=None,
        user_country=None,
        user_timezone=None,
        sec_ch_ua=None,
        sec_ch_ua_mobile=None,
        sec_ch_ua_platform=None,
    )

    # Test 3: authorization header
    req_auth = MagicMock()
    req_auth.headers = {"authorization": "SAPISIDHASH 12345_hash"}
    req_auth.query_params = {}
    req_auth.client = None
    YTMusicClient.get_client_from_request(req_auth)
    mock_get_client.assert_called_with(
        cookie_or_auth="SAPISIDHASH 12345_hash",
        language=None,
        user_agent=None,
        user_ip=None,
        user_country=None,
        user_timezone=None,
        sec_ch_ua=None,
        sec_ch_ua_mobile=None,
        sec_ch_ua_platform=None,
    )

    # Test 4: cookie query param
    req_query = MagicMock()
    req_query.headers = {}
    req_query.query_params = {"cookie": "query_cookie_val"}
    req_query.client = None
    YTMusicClient.get_client_from_request(req_query)
    mock_get_client.assert_called_with(
        cookie_or_auth="query_cookie_val",
        language=None,
        user_agent=None,
        user_ip=None,
        user_country=None,
        user_timezone=None,
        sec_ch_ua=None,
        sec_ch_ua_mobile=None,
        sec_ch_ua_platform=None,
    )


def test_fastapi_endpoint_receives_cookie(monkeypatch):
    mock_ytmusic_instance = MagicMock()
    mock_ytmusic_instance.get_home.return_value = [{"title": "User Personal Feed"}]

    def mock_get_client(cookie_or_auth=None, **_kwargs):
        if cookie_or_auth == "user_secret_cookie":
            return mock_ytmusic_instance
        default_inst = MagicMock()
        default_inst.get_home.return_value = [{"title": "Default Feed"}]
        return default_inst

    monkeypatch.setattr(YTMusicClient, "get_client", mock_get_client)

    test_client = TestClient(app)

    # 1. Request without cookie
    res_default = test_client.get("/browse/home")
    assert res_default.status_code == 200
    assert res_default.json()["result"][0]["title"] == "Default Feed"

    # 2. Request with custom x-ytmusic-cookie
    res_user = test_client.get("/browse/home", headers={"x-ytmusic-cookie": "user_secret_cookie"})
    assert res_user.status_code == 200
    assert res_user.json()["result"][0]["title"] == "User Personal Feed"
