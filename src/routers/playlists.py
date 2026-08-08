import logging

from fastapi import APIRouter, Depends, HTTPException
from ytmusicapi import YTMusic

from src.utils.client import get_ytmusic
from src.utils.error_handlers import handle_playlist_errors

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{playlistId}")
@handle_playlist_errors
def get_playlist(
    playlistId: str,
    limit: int | None = 100,
    related: bool = False,
    suggestions_limit: int = 0,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    results = ytmusic.get_playlist(
        playlistId, limit=limit, related=related, suggestions_limit=suggestions_limit
    )

    if not results:
        raise HTTPException(status_code=404, detail="Playlist not found")

    return {"message": "OK", "playlistId": playlistId, "result": results}


@router.post("/")
@handle_playlist_errors
async def create_playlist(
    title: str,
    description: str,
    privacy_status: str = "PRIVATE",
    video_ids: list | None = None,
    source_playlist: str | None = None,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    # Validate privacy status
    valid_privacy = ["PRIVATE", "PUBLIC", "UNLISTED"]
    if privacy_status not in valid_privacy:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid privacy_status '{privacy_status}'. "
                f"Must be one of: {', '.join(valid_privacy)}"
            ),
        )

    if not title.strip():
        raise HTTPException(status_code=400, detail="Playlist title cannot be empty")

    results = ytmusic.create_playlist(
        title,
        description,
        privacy_status=privacy_status,
        video_ids=video_ids,
        source_playlist=source_playlist,
    )

    return {
        "message": "OK",
        "title": title,
        "privacy_status": privacy_status,
        "result": results,
    }


@router.patch("/")
@handle_playlist_errors
# pylint: disable=too-many-positional-arguments
async def edit_playlist(
    playlistId: str,
    title: str | None = None,
    description: str | None = None,
    privacyStatus: str | None = None,
    moveItem: str | tuple[str, str] | None = None,
    addPlaylistId: str | None = None,
    addToTop: bool | None = None,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    # Validate privacy status if provided
    if privacyStatus:
        valid_privacy = ["PRIVATE", "PUBLIC", "UNLISTED"]
        if privacyStatus not in valid_privacy:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid privacyStatus '{privacyStatus}'. "
                    f"Must be one of: {', '.join(valid_privacy)}"
                ),
            )

    # Validate that at least one parameter is provided for editing
    if not any([title, description, privacyStatus, moveItem, addPlaylistId]):
        raise HTTPException(
            status_code=400,
            detail=(
                "At least one parameter (title, description, privacyStatus, "
                "moveItem, addPlaylistId) must be provided"
            ),
        )

    results = ytmusic.edit_playlist(
        playlistId,
        title=title,
        description=description,
        privacyStatus=privacyStatus,
        moveItem=moveItem,
        addPlaylistId=addPlaylistId,
        addToTop=addToTop,
    )

    return {"message": "OK", "playlistId": playlistId, "result": results}


@router.delete("/{playlistId}")
@handle_playlist_errors
async def delete_playlist(
    playlistId: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
    results = ytmusic.delete_playlist(playlistId)

    return {"message": "OK", "playlistId": playlistId, "result": results}


@router.post("/items")
@handle_playlist_errors
async def add_playlist_items(
    playlistId: str,
    videoIds: list[str] | None = None,
    source_playlist: str | None = None,
    duplicates: bool = False,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    # Validate input
    if not videoIds and not source_playlist:
        raise HTTPException(
            status_code=400, detail="Either videoIds or source_playlist must be provided"
        )

    if videoIds is not None and not videoIds:
        raise HTTPException(status_code=400, detail="videoIds cannot be empty if provided")

    results = ytmusic.add_playlist_items(
        playlistId, videoIds=videoIds, source_playlist=source_playlist, duplicates=duplicates
    )

    return {
        "message": "OK",
        "playlistId": playlistId,
        "videoIds": videoIds,
        "source_playlist": source_playlist,
        "result": results,
    }


@router.delete("/items/{playlistId}")
@handle_playlist_errors
async def remove_playlist_items(
    playlistId: str,
    videos: list[dict],
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    if not videos:
        raise HTTPException(
            status_code=400, detail="At least one video must be provided for removal"
        )

    results = ytmusic.remove_playlist_items(playlistId, videos)

    return {
        "message": "OK",
        "playlistId": playlistId,
        "videos_count": len(videos),
        "result": results,
    }

