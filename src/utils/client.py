"""
Centralized YTMusic client manager to share a single client instance
and session across all API endpoints, improving performance via HTTP connection pooling.
"""

import logging
from typing import Any

import ytmusicapi.mixins.playlists
import ytmusicapi.parsers.playlists
from ytmusicapi import YTMusic
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

    @classmethod
    def get_client(cls) -> YTMusic:
        """
        Gets the singleton YTMusic client instance. Lazily initializes it.
        """
        if cls._instance is None:
            logger.info("Initializing global YTMusic client instance")
            try:
                cls._instance = YTMusic()
            except Exception as e:
                logger.error("Failed to initialize global YTMusic client: %s", e)
                # Fallback to simple instantiation if anything goes wrong
                cls._instance = YTMusic()
        return cls._instance

    @classmethod
    def reset_client(cls) -> None:
        """
        Resets the client instance (useful for testing or re-initialization).
        """
        cls._instance = None
