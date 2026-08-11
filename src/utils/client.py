"""
Centralized YTMusic client manager to share a single client instance
and session across all API endpoints, improving performance via HTTP connection pooling.
"""

import hashlib
import json
import logging
from typing import Any

from fastapi import Request
import ytmusicapi.mixins.playlists
import ytmusicapi.parsers.playlists
from ytmusicapi import YTMusic, setup
from ytmusicapi.helpers import initialize_headers


from ytmusicapi.continuations import get_continuations_2025
from ytmusicapi.helpers import sum_total_duration
from ytmusicapi.navigation import (
    CONTENT,
    MRLIR,
    PLAY_BUTTON,
    SECTION,
    TWO_COLUMN_RENDERER,
    WATCH_PLAYLIST_ID,
    nav,
)

logger = logging.getLogger(__name__)


# Safe parse audio playlist to handle tracks with no albums
def safe_parse_audio_playlist(response: dict, limit: int | None, request_func: Any) -> dict:
    """
    Safe wrapper for parse_audio_playlist to handle playlists/albums
    where the first track or subsequent tracks lack album information.
    """
    playlist: dict = {
        "owned": False,
        "privacy": "PUBLIC",
        "description": None,
        "views": None,
        "duration": None,
        "tracks": [],
        "thumbnails": [],
        "related": [],
    }

    try:
        section_list = nav(response, [*TWO_COLUMN_RENDERER, "secondaryContents", *SECTION])
        content_data = nav(section_list, [*CONTENT, "musicPlaylistShelfRenderer"])

        playlist["id"] = nav(
            content_data,
            [
                *CONTENT,
                MRLIR,
                *PLAY_BUTTON,
                "playNavigationEndpoint",
                *WATCH_PLAYLIST_ID,
            ],
        )
        playlist["trackCount"] = nav(content_data, ["collapsedItemCount"])

        playlist["tracks"] = []
        if "contents" in content_data:
            playlist["tracks"] = ytmusicapi.parsers.playlists.parse_playlist_items(
                content_data["contents"]
            )

            parse_func = ytmusicapi.parsers.playlists.parse_playlist_items
            playlist["tracks"].extend(
                get_continuations_2025(content_data, limit, request_func, parse_func)
            )

        # Safe extraction of title
        title = "Unknown Album"
        if playlist["tracks"]:
            first_track = playlist["tracks"][0]
            if "album" in first_track and first_track["album"] and "name" in first_track["album"]:
                title = first_track["album"]["name"]
            elif "title" in first_track:
                title = first_track["title"]
        playlist["title"] = title

        playlist["duration_seconds"] = sum_total_duration(playlist)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.warning("Error parsing audio playlist: %s. Using basic fallback.", e)
        playlist["title"] = playlist.get("title") or "Unknown Album"
        playlist["duration_seconds"] = playlist.get("duration_seconds") or 0

    return playlist


# Apply monkeypatches immediately
ytmusicapi.parsers.playlists.parse_audio_playlist = safe_parse_audio_playlist
ytmusicapi.mixins.playlists.parse_audio_playlist = safe_parse_audio_playlist
logger.info("Successfully applied monkeypatch to ytmusicapi.parse_audio_playlist")


SUPPORTED_YTMUSIC_LANGS = {
    "tr", "nl", "en", "pt", "cs", "ja", "ur", "ar",
    "zh_CN", "fr", "ru", "zh_TW", "ko", "hi", "de", "es", "it"
}


def normalize_yt_language(lang_str: str | None) -> tuple[str, str | None]:
    """
    Parses incoming Accept-Language / lang string (e.g. 'th-TH,th;q=0.9,en-US;q=0.8' or 'ja-JP').
    Returns a tuple of (ytmusicapi_supported_lang, raw_accept_language_header).
    """
    if not lang_str:
        return "en", None

    raw_accept_lang = lang_str.strip()
    first_part = raw_accept_lang.split(",")[0].split(";")[0].strip()
    tag = first_part.replace("-", "_")

    if tag.lower() in {"zh_cn", "zh_hans"}:
        matched_lang = "zh_CN"
    elif tag.lower() in {"zh_tw", "zh_hk", "zh_hant"}:
        matched_lang = "zh_TW"
    else:
        primary = tag.split("_")[0].lower()
        if primary in SUPPORTED_YTMUSIC_LANGS:
            matched_lang = primary
        else:
            matched_lang = "en"

    return matched_lang, raw_accept_lang


class YTMusicClient:
    _instance = None
    _cookie_clients: dict[str, YTMusic] = {}
    _max_cache_size: int = 200

    @classmethod
    def get_client(
        cls,
        cookie_or_auth: str | dict | None = None,
        language: str | None = None,
        user_agent: str | None = None,
        user_ip: str | None = None,
        user_country: str | None = None,
        user_timezone: str | None = None,
        sec_ch_ua: str | None = None,
        sec_ch_ua_mobile: str | None = None,
        sec_ch_ua_platform: str | None = None,
    ) -> YTMusic:
        """
        Gets a YTMusic client instance with dynamic user metadata support.
        Configures user auth, user-agent, language, country, timezone, client hints,
        and IP forwarding headers on the client session.
        """
        yt_lang, accept_lang_header = normalize_yt_language(language)

        if isinstance(cookie_or_auth, dict):
            auth_key_str = str(cookie_or_auth)
        elif cookie_or_auth:
            auth_key_str = cookie_or_auth.strip()
        else:
            auth_key_str = "anonymous"

        auth_hash = hashlib.sha256(auth_key_str.encode("utf-8")).hexdigest()[:16]
        ua_hash = hashlib.sha256((user_agent or "default").encode("utf-8")).hexdigest()[:8]
        country_hash = (user_country or "default").lower()
        cache_key = f"{auth_hash}:{yt_lang}:{country_hash}:{ua_hash}"

        if cache_key in cls._cookie_clients:
            client = cls._cookie_clients[cache_key]
            if user_ip:
                client._session.headers["X-Forwarded-For"] = user_ip
                client._session.headers["X-User-IP"] = user_ip
            return client

        logger.info(
            "Initializing metadata-scoped YTMusic client (key: %s, lang: %s, country: %s, ip: %s)",
            cache_key,
            yt_lang,
            user_country or "none",
            user_ip or "none",
        )
        try:
            client_instance = cls._build_user_client(
                cookie_or_auth=cookie_or_auth if auth_key_str != "anonymous" else None,
                language=yt_lang,
                accept_language=accept_lang_header,
                user_agent=user_agent,
                user_ip=user_ip,
                user_country=user_country,
                user_timezone=user_timezone,
                sec_ch_ua=sec_ch_ua,
                sec_ch_ua_mobile=sec_ch_ua_mobile,
                sec_ch_ua_platform=sec_ch_ua_platform,
            )
            if len(cls._cookie_clients) >= cls._max_cache_size:
                oldest_key = next(iter(cls._cookie_clients))
                del cls._cookie_clients[oldest_key]
            cls._cookie_clients[cache_key] = client_instance
            return client_instance
        except Exception as e:
            logger.warning(
                "Failed to initialize custom YTMusic client (%s). Falling back to default client.",
                e,
            )
            if cls._instance is None:
                cls._instance = YTMusic(language=yt_lang)
            return cls._instance

    @classmethod
    def _build_user_client(
        cls,
        cookie_or_auth: str | dict | None = None,
        language: str = "en",
        accept_language: str | None = None,
        user_agent: str | None = None,
        user_ip: str | None = None,
        user_country: str | None = None,
        user_timezone: str | None = None,
        sec_ch_ua: str | None = None,
        sec_ch_ua_mobile: str | None = None,
        sec_ch_ua_platform: str | None = None,
    ) -> YTMusic:
        """Helper to build a YTMusic client with metadata session headers."""
        client: YTMusic | None = None

        if isinstance(cookie_or_auth, dict):
            client = YTMusic(auth=cookie_or_auth, language=language)
        elif cookie_or_auth:
            auth_str = cookie_or_auth.strip()
            if auth_str.startswith("{"):
                try:
                    auth_dict = json.loads(auth_str)
                    client = YTMusic(auth=auth_dict, language=language)
                except Exception:
                    client = None

            if client is None and "\n" in auth_str and ":" in auth_str:
                try:
                    parsed_json_str = setup(headers_raw=auth_str)
                    client = YTMusic(auth=parsed_json_str, language=language)
                except Exception:
                    client = None

            if client is None:
                headers = dict(initialize_headers())
                headers["cookie"] = auth_str
                headers["x-goog-authuser"] = "0"
                client = YTMusic(auth=headers, language=language)
        else:
            client = YTMusic(language=language)

        if user_agent:
            client._session.headers["User-Agent"] = user_agent
            client.headers["user-agent"] = user_agent

        if accept_language:
            client._session.headers["Accept-Language"] = accept_language

        if user_ip:
            client._session.headers["X-Forwarded-For"] = user_ip
            client._session.headers["X-User-IP"] = user_ip
            client._session.headers["X-Originating-IP"] = user_ip

        if user_country:
            client._session.headers["X-User-Country"] = user_country.upper()
            if hasattr(client, "context") and isinstance(client.context, dict):
                client.context.setdefault("context", {}).setdefault("client", {})["gl"] = user_country.upper()

        if user_timezone:
            client._session.headers["X-Time-Zone"] = user_timezone
            if hasattr(client, "context") and isinstance(client.context, dict):
                client.context.setdefault("context", {}).setdefault("client", {})["timeZone"] = user_timezone

        if sec_ch_ua:
            client._session.headers["Sec-CH-UA"] = sec_ch_ua
        if sec_ch_ua_mobile:
            client._session.headers["Sec-CH-UA-Mobile"] = sec_ch_ua_mobile
        if sec_ch_ua_platform:
            client._session.headers["Sec-CH-UA-Platform"] = sec_ch_ua_platform

        return client

    @classmethod
    def get_auth_key_from_request(cls, request: Request) -> str | None:
        """Returns candidate cookie/auth string from Request, or None if unauthenticated."""
        if "x-ytmusic-cookie" in request.headers:
            return request.headers["x-ytmusic-cookie"]
        if "cookie" in request.headers:
            return request.headers["cookie"]
        if "authorization" in request.headers:
            return request.headers["authorization"]
        if "cookie" in request.query_params:
            return request.query_params["cookie"]
        return None

    @classmethod
    def get_request_user_lang(cls, request: Request) -> str | None:
        """Extracts candidate language string from Request headers or query parameters."""
        if "x-user-lang" in request.headers:
            return request.headers["x-user-lang"]
        if "accept-language" in request.headers:
            return request.headers["accept-language"]
        if "hl" in request.query_params:
            return request.query_params["hl"]
        return None

    @classmethod
    def get_request_user_country(cls, request: Request) -> str | None:
        """Extracts country/region code from Request headers or query parameters."""
        if "x-user-country" in request.headers:
            return request.headers["x-user-country"]
        if "gl" in request.query_params:
            return request.query_params["gl"]
        if "cf-ipcountry" in request.headers:
            return request.headers["cf-ipcountry"]
        return None

    @classmethod
    def get_request_user_timezone(cls, request: Request) -> str | None:
        """Extracts timezone identifier or offset from Request headers."""
        if "x-user-timezone" in request.headers:
            return request.headers["x-user-timezone"]
        if "x-time-zone" in request.headers:
            return request.headers["x-time-zone"]
        return None

    @classmethod
    def get_request_user_agent(cls, request: Request) -> str | None:
        """Extracts candidate user agent string from Request headers."""
        if "x-user-agent" in request.headers:
            return request.headers["x-user-agent"]
        if "user-agent" in request.headers:
            return request.headers["user-agent"]
        return None

    @classmethod
    def get_request_user_ip(cls, request: Request) -> str | None:
        """Extracts candidate client IP from Request headers or connection state."""
        if "x-forwarded-for" in request.headers:
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        if "x-real-ip" in request.headers:
            return request.headers["x-real-ip"].strip()
        if request.client and request.client.host:
            return request.client.host
        return None

    @classmethod
    def get_client_from_request(cls, request: Request) -> YTMusic:
        """
        Extracts user cookie/auth, language, country, timezone, user-agent, client hints, and IP
        from incoming FastAPI Request and returns the appropriate client.
        """
        cookie_candidate = cls.get_auth_key_from_request(request)
        user_lang = cls.get_request_user_lang(request)
        user_country = cls.get_request_user_country(request)
        user_timezone = cls.get_request_user_timezone(request)
        user_agent = cls.get_request_user_agent(request)
        user_ip = cls.get_request_user_ip(request)

        sec_ch_ua = request.headers.get("sec-ch-ua")
        sec_ch_ua_mobile = request.headers.get("sec-ch-ua-mobile")
        sec_ch_ua_platform = request.headers.get("sec-ch-ua-platform")

        return cls.get_client(
            cookie_or_auth=cookie_candidate,
            language=user_lang,
            user_agent=user_agent,
            user_ip=user_ip,
            user_country=user_country,
            user_timezone=user_timezone,
            sec_ch_ua=sec_ch_ua,
            sec_ch_ua_mobile=sec_ch_ua_mobile,
            sec_ch_ua_platform=sec_ch_ua_platform,
        )

    @classmethod
    def reset_client(cls) -> None:
        """
        Resets all client instances (useful for testing or re-initialization).
        """
        cls._instance = None
        cls._cookie_clients.clear()


def get_ytmusic(request: Request) -> YTMusic:
    """FastAPI dependency for injecting per-user YTMusic client."""
    return YTMusicClient.get_client_from_request(request)


def get_request_auth_key(request: Request) -> str | None:
    """Helper to get user auth key or None for caching purposes."""
    return YTMusicClient.get_auth_key_from_request(request)


def get_request_user_lang(request: Request) -> str | None:
    """Helper to get user language or None for caching purposes."""
    return YTMusicClient.get_request_user_lang(request)

