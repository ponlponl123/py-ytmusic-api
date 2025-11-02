import logging

from fastapi import APIRouter, HTTPException
from ytmusicapi import YTMusic

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{playlistId}")
def get_playlist(
    playlistId: str, limit: int | None = 100, related: bool = False, suggestions_limit: int = 0
):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_playlist(
            playlistId, limit=limit, related=related, suggestions_limit=suggestions_limit
        )

        if not results:
            raise HTTPException(status_code=404, detail="Playlist not found")

        return {"message": "OK", "playlistId": playlistId, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_playlist for {playlistId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, playlist data temporarily unavailable",
                "playlistId": playlistId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_playlist for {playlistId}: {str(e)}")
        if "not found" in str(e).lower() or "unavailable" in str(e).lower():
            raise HTTPException(
                status_code=404, detail=f"Playlist with ID {playlistId} not found or unavailable"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching playlist",
                "playlistId": playlistId,
            },
        )


@router.post("/")
async def create_playlist(
    title: str,
    description: str,
    privacy_status: str = "PRIVATE",
    video_ids: list | None = None,
    source_playlist: str | None = None,
):
    try:
        # Validate privacy status
        valid_privacy = ["PRIVATE", "PUBLIC", "UNLISTED"]
        if privacy_status not in valid_privacy:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid privacy_status '{privacy_status}'. Must be one of: {', '.join(valid_privacy)}",
            )

        if not title.strip():
            raise HTTPException(status_code=400, detail="Playlist title cannot be empty")

        ytmusic = YTMusic()
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

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in create_playlist for '{title}': {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot create playlist",
                "title": title,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in create_playlist for '{title}': {str(e)}")
        if "auth" in str(e).lower() or "login" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to create playlists"
            )
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            raise HTTPException(status_code=429, detail="Rate limit exceeded or quota reached")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while creating playlist",
                "title": title,
            },
        )


@router.patch("/")
async def edit_playlist(
    playlistId: str,
    title: str | None = None,
    description: str | None = None,
    privacyStatus: str | None = None,
    moveItem: str | tuple[str, str] | None = None,
    addPlaylistId: str | None = None,
    addToTop: bool | None = None,
):
    try:
        # Validate privacy status if provided
        if privacyStatus:
            valid_privacy = ["PRIVATE", "PUBLIC", "UNLISTED"]
            if privacyStatus not in valid_privacy:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid privacyStatus '{privacyStatus}'. Must be one of: {', '.join(valid_privacy)}",
                )

        # Validate that at least one parameter is provided for editing
        if not any([title, description, privacyStatus, moveItem, addPlaylistId]):
            raise HTTPException(
                status_code=400,
                detail="At least one parameter (title, description, privacyStatus, moveItem, addPlaylistId) must be provided",
            )

        ytmusic = YTMusic()
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

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in edit_playlist for {playlistId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot edit playlist",
                "playlistId": playlistId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in edit_playlist for {playlistId}: {str(e)}")
        if "auth" in str(e).lower() or "login" in str(e).lower():
            raise HTTPException(status_code=401, detail="Authentication required to edit playlists")
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Playlist with ID {playlistId} not found")
        elif "permission" in str(e).lower():
            raise HTTPException(
                status_code=403, detail="You don't have permission to edit this playlist"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while editing playlist",
                "playlistId": playlistId,
            },
        )


@router.delete("/{playlistId}")
async def delete_playlist(playlistId: str):
    try:
        ytmusic = YTMusic()
        results = ytmusic.delete_playlist(playlistId)

        return {"message": "OK", "playlistId": playlistId, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in delete_playlist for {playlistId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot delete playlist",
                "playlistId": playlistId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in delete_playlist for {playlistId}: {str(e)}")
        if "auth" in str(e).lower() or "login" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to delete playlists"
            )
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Playlist with ID {playlistId} not found")
        elif "permission" in str(e).lower():
            raise HTTPException(
                status_code=403, detail="You don't have permission to delete this playlist"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while deleting playlist",
                "playlistId": playlistId,
            },
        )


@router.post("/items")
async def add_playlist_items(
    playlistId: str,
    videoIds: list[str] | None = None,
    source_playlist: str | None = None,
    duplicates: bool = False,
):
    try:
        # Validate input
        if not videoIds and not source_playlist:
            raise HTTPException(
                status_code=400, detail="Either videoIds or source_playlist must be provided"
            )

        if videoIds and not videoIds:
            raise HTTPException(status_code=400, detail="videoIds cannot be empty if provided")

        ytmusic = YTMusic()
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

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in add_playlist_items for {playlistId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot add playlist items",
                "playlistId": playlistId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in add_playlist_items for {playlistId}: {str(e)}")
        if "auth" in str(e).lower() or "login" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to add playlist items"
            )
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Playlist with ID {playlistId} not found")
        elif "permission" in str(e).lower():
            raise HTTPException(
                status_code=403, detail="You don't have permission to edit this playlist"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while adding playlist items",
                "playlistId": playlistId,
            },
        )


@router.delete("/items/{playlistId}")
async def remove_playlist_items(playlistId: str, videos: list[dict]):
    try:
        if not videos:
            raise HTTPException(
                status_code=400, detail="At least one video must be provided for removal"
            )

        ytmusic = YTMusic()
        results = ytmusic.remove_playlist_items(playlistId, videos)

        return {
            "message": "OK",
            "playlistId": playlistId,
            "videos_count": len(videos),
            "result": results,
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in remove_playlist_items for {playlistId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot remove playlist items",
                "playlistId": playlistId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in remove_playlist_items for {playlistId}: {str(e)}")
        if "auth" in str(e).lower() or "login" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to remove playlist items"
            )
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Playlist with ID {playlistId} not found")
        elif "permission" in str(e).lower():
            raise HTTPException(
                status_code=403, detail="You don't have permission to edit this playlist"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while removing playlist items",
                "playlistId": playlistId,
            },
        )
