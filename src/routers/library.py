import logging
from typing import Literal

from fastapi import APIRouter, HTTPException

from src.utils.client import YTMusicClient
from src.utils.error_handlers import handle_library_errors

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/library_playlists")
@handle_library_errors
async def get_library_playlists(limit: int | None = 25):
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.get_library_playlists(limit)
    return {"message": "OK", "result": results}


@router.get("/library_songs")
@handle_library_errors
async def get_library_songs(
    limit: int = 25,
    validate_responses: bool = False,
    order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None,
):
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.get_library_songs(limit, validate_responses, order)
    return {"message": "OK", "result": results}


@router.get("/library_albums")
@handle_library_errors
async def get_library_albums(
    limit: int = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.get_library_albums(limit, order)
    return {"message": "OK", "result": results}


@router.get("/library_artists")
@handle_library_errors
async def get_library_artists(
    limit: int = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.get_library_artists(limit, order)
    return {"message": "OK", "result": results}


@router.get("/library_subscriptions")
@handle_library_errors
async def get_library_subscriptions(
    limit: int = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.get_library_subscriptions(limit, order)
    return {"message": "OK", "result": results}


@router.get("/library_podcasts")
@handle_library_errors
async def get_library_podcasts(
    limit: int = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.get_library_podcasts(limit, order)
    return {"message": "OK", "result": results}


@router.get("/library_channels")
@handle_library_errors
async def get_library_channels(
    limit: int = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.get_library_channels(limit, order)
    return {"message": "OK", "result": results}


@router.get("/liked_songs")
@handle_library_errors
async def get_liked_songs(limit: int = 100):
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.get_liked_songs(limit)
    return {"message": "OK", "result": results}


@router.get("/saved_episodes")
@handle_library_errors
async def get_saved_episodes(limit: int = 100):
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.get_saved_episodes(limit)
    return {"message": "OK", "result": results}


@router.get("/history")
@handle_library_errors
async def get_history():
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.get_history()
    return {"message": "OK", "result": results}


@router.get("/account_info")
@handle_library_errors
async def get_account_info():
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.get_account_info()
    return {"message": "OK", "result": results}


@router.post("/history/{videoId}")
@handle_library_errors
async def add_history_item(videoId: str):
    ytmusic = YTMusicClient.get_client()
    song = ytmusic.get_song(videoId)

    if not song:
        raise HTTPException(status_code=404, detail=f"Song with ID {videoId} not found")

    results = ytmusic.add_history_item(song)
    return {"message": "OK", "videoId": videoId, "result": results}


@router.delete("/history")
@handle_library_errors
async def remove_history_items(feedbackTokens: list[str]):
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.remove_history_items(feedbackTokens)
    return {"message": "OK", "feedbackTokens": feedbackTokens, "result": results}


@router.post("/rate_song/{videoId}")
@handle_library_errors
async def rate_song(videoId: str, rating: str = "INDIFFERENT"):
    valid_ratings = ["LIKE", "DISLIKE", "INDIFFERENT"]
    if rating not in valid_ratings:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid rating '{rating}'. Must be one of: {', '.join(valid_ratings)}",
        )

    ytmusic = YTMusicClient.get_client()
    results = ytmusic.rate_song(videoId, rating)
    return {"message": "OK", "videoId": videoId, "rating": rating, "result": results}


@router.post("/rate_playlist/{playlistId}")
@handle_library_errors
async def rate_playlist(playlistId: str, rating: str = "INDIFFERENT"):
    valid_ratings = ["LIKE", "DISLIKE", "INDIFFERENT"]
    if rating not in valid_ratings:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid rating '{rating}'. Must be one of: {', '.join(valid_ratings)}",
        )

    ytmusic = YTMusicClient.get_client()
    results = ytmusic.rate_playlist(playlistId, rating)
    return {"message": "OK", "playlistId": playlistId, "rating": rating, "result": results}


@router.post("/subscribe_artists")
@handle_library_errors
async def subscribe_artists(channelIds: list[str]):
    if not channelIds:
        raise HTTPException(status_code=400, detail="At least one channel ID is required")

    ytmusic = YTMusicClient.get_client()
    results = ytmusic.subscribe_artists(channelIds)
    return {"message": "OK", "channelIds": channelIds, "result": results}


@router.delete("/subscribe_artists")
@handle_library_errors
async def unsubscribe_artists(channelIds: list[str]):
    if not channelIds:
        raise HTTPException(status_code=400, detail="At least one channel ID is required")

    ytmusic = YTMusicClient.get_client()
    results = ytmusic.unsubscribe_artists(channelIds)
    return {"message": "OK", "channelIds": channelIds, "result": results}


@router.patch("/song_library_status")
@handle_library_errors
async def edit_song_library_status(feedbackTokens: list[str]):
    if not feedbackTokens:
        raise HTTPException(status_code=400, detail="At least one feedback token is required")

    ytmusic = YTMusicClient.get_client()
    results = ytmusic.edit_song_library_status(feedbackTokens)
    return {"message": "OK", "feedbackTokens": feedbackTokens, "result": results}
