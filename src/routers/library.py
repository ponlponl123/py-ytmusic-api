import logging
from typing import Callable, Literal

from fastapi import APIRouter, HTTPException
from ytmusicapi import YTMusic

router = APIRouter()
logger = logging.getLogger(__name__)


def handle_ytmusic_errors(operation_name: str, identifier: str = None):
    """Decorator to handle common YTMusic API errors"""

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)

            except KeyError as e:
                logger.error("KeyError in %s: %s", operation_name, str(e))
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "API structure error",
                        "message": f"YouTube Music API structure has changed, {operation_name.replace('_', ' ')} temporarily unavailable",
                        "technical_details": str(e),
                    },
                ) from e

            except Exception as e:
                logger.error("Unexpected error in %s: %s", operation_name, str(e))
                if "auth" in str(e).lower() or "login" in str(e).lower():
                    raise HTTPException(
                        status_code=401,
                        detail=f"Authentication required to access {operation_name.replace('_', ' ')}",
                    ) from e
                if "not found" in str(e).lower():
                    raise HTTPException(
                        status_code=404,
                        detail=f"Content not found for {operation_name.replace('_', ' ')}",
                    ) from e

                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Internal server error",
                        "message": f"An unexpected error occurred while {operation_name.replace('_', ' ')}",
                    },
                ) from e

        return wrapper

    return decorator


@router.get("/library_playlists")
async def get_library_playlists(limit: int | None = 25):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_library_playlists(limit)

        return {"message": "OK", "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_library_playlists: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, library playlists temporarily unavailable",
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_library_playlists: {str(e)}")
        if "auth" in str(e).lower() or "login" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to access library playlists"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching library playlists",
            },
        )


@router.get("/library_songs")
async def get_library_songs(
    limit: int = 25,
    validate_responses: bool = False,
    order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None,
):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_library_songs(limit, validate_responses, order)

        return {"message": "OK", "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_library_songs: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, library songs temporarily unavailable",
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_library_songs: {str(e)}")
        if "auth" in str(e).lower() or "login" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to access library songs"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching library songs",
            },
        )


@router.get("/library_albums")
@handle_ytmusic_errors("get_library_albums")
async def get_library_albums(
    limit: int = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusic()
    results = ytmusic.get_library_albums(limit, order)

    return {"message": "OK", "result": results}


@router.get("/library_artists")
@handle_ytmusic_errors("get_library_artists")
async def get_library_artists(
    limit: int = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusic()
    results = ytmusic.get_library_artists(limit, order)

    return {"message": "OK", "result": results}


@router.get("/library_subscriptions")
@handle_ytmusic_errors("get_library_subscriptions")
async def get_library_subscriptions(
    limit: int = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusic()
    results = ytmusic.get_library_subscriptions(limit, order)

    return {"message": "OK", "result": results}


@router.get("/library_podcasts")
@handle_ytmusic_errors("get_library_podcasts")
async def get_library_podcasts(
    limit: int = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusic()
    results = ytmusic.get_library_podcasts(limit, order)

    return {"message": "OK", "result": results}


@router.get("/library_channels")
@handle_ytmusic_errors("get_library_channels")
async def get_library_channels(
    limit: int = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusic()
    results = ytmusic.get_library_channels(limit, order)

    return {"message": "OK", "result": results}


@router.get("/liked_songs")
@handle_ytmusic_errors("get_liked_songs")
async def get_liked_songs(limit: int = 100):
    ytmusic = YTMusic()
    results = ytmusic.get_liked_songs(limit)

    return {"message": "OK", "result": results}


@router.get("/saved_episodes")
@handle_ytmusic_errors("get_saved_episodes")
async def get_saved_episodes(limit: int = 100):
    ytmusic = YTMusic()
    results = ytmusic.get_saved_episodes(limit)

    return {"message": "OK", "result": results}


@router.get("/history")
@handle_ytmusic_errors("get_history")
async def get_history():
    ytmusic = YTMusic()
    results = ytmusic.get_history()

    return {"message": "OK", "result": results}


@router.get("/account_info")
@handle_ytmusic_errors("get_account_info")
async def get_account_info():
    ytmusic = YTMusic()
    results = ytmusic.get_account_info()

    return {"message": "OK", "result": results}


@router.post("/history/{videoId}")
async def add_history_item(videoId: str):
    try:
        ytmusic = YTMusic()
        song = ytmusic.get_song(videoId)

        if not song:
            raise HTTPException(status_code=404, detail=f"Song with ID {videoId} not found")

        results = ytmusic.add_history_item(song)

        return {"message": "OK", "videoId": videoId, "result": results}

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in add_history_item for {videoId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot add to history",
                "videoId": videoId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in add_history_item for {videoId}: {str(e)}")
        if "auth" in str(e).lower():
            raise HTTPException(status_code=401, detail="Authentication required to add to history")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while adding to history",
                "videoId": videoId,
            },
        )


@router.delete("/history")
async def remove_history_items(feedbackTokens: list[str]):
    try:
        ytmusic = YTMusic()
        results = ytmusic.remove_history_items(feedbackTokens)

        return {"message": "OK", "feedbackTokens": feedbackTokens, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in remove_history_items: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot remove history items",
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in remove_history_items: {str(e)}")
        if "auth" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to remove history items"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while removing history items",
            },
        )


@router.post("/rate_song/{videoId}")
async def rate_song(videoId: str, rating: str = "INDIFFERENT"):
    try:
        valid_ratings = ["LIKE", "DISLIKE", "INDIFFERENT"]
        if rating not in valid_ratings:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid rating '{rating}'. Must be one of: {', '.join(valid_ratings)}",
            )

        ytmusic = YTMusic()
        results = ytmusic.rate_song(videoId, rating)

        return {"message": "OK", "videoId": videoId, "rating": rating, "result": results}

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in rate_song for {videoId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot rate song",
                "videoId": videoId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in rate_song for {videoId}: {str(e)}")
        if "auth" in str(e).lower():
            raise HTTPException(status_code=401, detail="Authentication required to rate songs")
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Song with ID {videoId} not found")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while rating song",
                "videoId": videoId,
            },
        )


@router.post("/rate_playlist/{playlistId}")
async def rate_playlist(playlistId: str, rating: str = "INDIFFERENT"):
    try:
        valid_ratings = ["LIKE", "DISLIKE", "INDIFFERENT"]
        if rating not in valid_ratings:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid rating '{rating}'. Must be one of: {', '.join(valid_ratings)}",
            )

        ytmusic = YTMusic()
        results = ytmusic.rate_playlist(playlistId, rating)

        return {"message": "OK", "playlistId": playlistId, "rating": rating, "result": results}

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in rate_playlist for {playlistId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot rate playlist",
                "playlistId": playlistId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in rate_playlist for {playlistId}: {str(e)}")
        if "auth" in str(e).lower():
            raise HTTPException(status_code=401, detail="Authentication required to rate playlists")
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Playlist with ID {playlistId} not found")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while rating playlist",
                "playlistId": playlistId,
            },
        )


@router.post("/subscribe_artists")
async def subscribe_artists(channelIds: list[str]):
    try:
        if not channelIds:
            raise HTTPException(status_code=400, detail="At least one channel ID is required")

        ytmusic = YTMusic()
        results = ytmusic.subscribe_artists(channelIds)

        return {"message": "OK", "channelIds": channelIds, "result": results}

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in subscribe_artists: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot subscribe to artists",
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in subscribe_artists: {str(e)}")
        if "auth" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to subscribe to artists"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while subscribing to artists",
                "channelIds": channelIds,
            },
        )


@router.delete("/subscribe_artists")
async def unsubscribe_artists(channelIds: list[str]):
    try:
        if not channelIds:
            raise HTTPException(status_code=400, detail="At least one channel ID is required")

        ytmusic = YTMusic()
        results = ytmusic.unsubscribe_artists(channelIds)

        return {"message": "OK", "channelIds": channelIds, "result": results}

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in unsubscribe_artists: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot unsubscribe from artists",
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in unsubscribe_artists: {str(e)}")
        if "auth" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to unsubscribe from artists"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while unsubscribing from artists",
                "channelIds": channelIds,
            },
        )


@router.patch("/song_library_status")
async def edit_song_library_status(feedbackTokens: list[str]):
    try:
        if not feedbackTokens:
            raise HTTPException(status_code=400, detail="At least one feedback token is required")

        ytmusic = YTMusic()
        results = ytmusic.edit_song_library_status(feedbackTokens)

        return {"message": "OK", "feedbackTokens": feedbackTokens, "result": results}

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in edit_song_library_status: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot edit song library status",
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in edit_song_library_status: {str(e)}")
        if "auth" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to edit song library status"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while editing song library status",
            },
        )
