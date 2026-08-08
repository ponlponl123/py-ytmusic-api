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


class YTMusicClient:
    _instance = None
    _cookie_clients: dict[str, YTMusic] = {}
    _max_cache_size: int = 200

    @classmethod
    def get_client(cls, cookie_or_auth: str | dict | None = None) -> YTMusic:
        """
        Gets a YTMusic client instance. If a cookie or auth dictionary/string is provided,
        initializes or retrieves a cached YTMusic instance for that specific user.
        Otherwise returns the default shared unauthenticated client.
        """
        if not cookie_or_auth:
            if cls._instance is None:
                logger.info("Initializing global YTMusic client instance")
                try:
                    cls._instance = YTMusic()
                except Exception as e:
                    logger.error("Failed to initialize global YTMusic client: %s", e)
                    cls._instance = YTMusic()
            return cls._instance

        # Normalize and hash auth key for caching
        if isinstance(cookie_or_auth, dict):
            auth_key_str = str(cookie_or_auth)
        else:
            auth_key_str = cookie_or_auth.strip()
        auth_hash = hashlib.sha256(auth_key_str.encode("utf-8")).hexdigest()

        if auth_hash in cls._cookie_clients:
            return cls._cookie_clients[auth_hash]

        logger.info("Initializing user-specific YTMusic client (hash: %s...)", auth_hash[:8])
        try:
            client_instance = cls._build_user_client(cookie_or_auth)
            # Evict oldest entry if cache exceeds maximum size
            if len(cls._cookie_clients) >= cls._max_cache_size:
                oldest_key = next(iter(cls._cookie_clients))
                del cls._cookie_clients[oldest_key]
            cls._cookie_clients[auth_hash] = client_instance
            return client_instance
        except Exception as e:
            logger.warning(
                "Failed to initialize custom YTMusic client (%s). Falling back to default client.",
                e,
            )
            return cls.get_client(None)

    @classmethod
    def _build_user_client(cls, cookie_or_auth: str | dict) -> YTMusic:
        """Helper to build a YTMusic client from a cookie string or auth dict/JSON."""
        if isinstance(cookie_or_auth, dict):
            return YTMusic(auth=cookie_or_auth)

        auth_str = cookie_or_auth.strip()

        # Case 1: JSON format string
        if auth_str.startswith("{"):
            try:
                auth_dict = json.loads(auth_str)
                return YTMusic(auth=auth_dict)
            except Exception:
                pass

        # Case 2: Raw browser header string (contains colons and newlines)
        if "\n" in auth_str and ":" in auth_str:
            try:
                parsed_json_str = setup(headers_raw=auth_str)
                return YTMusic(auth=parsed_json_str)
            except Exception:
                pass

        # Case 3: Standard cookie string (e.g., SAPISID=... or VISITOR_INFO1_LIVE=...)
        headers = dict(initialize_headers())
        headers["cookie"] = auth_str
        headers["x-goog-authuser"] = "0"
        return YTMusic(auth=headers)

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
    def get_client_from_request(cls, request: Request) -> YTMusic:
        """
        Extracts user cookie/auth from incoming FastAPI Request and returns the appropriate client.
        Checks:
        1. x-ytmusic-cookie header
        2. cookie header / request cookies
        3. authorization header
        4. cookie query parameter
        """
        cookie_candidate = cls.get_auth_key_from_request(request)
        return cls.get_client(cookie_candidate)

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
