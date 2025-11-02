import logging

from fastapi import APIRouter, HTTPException
from ytmusicapi import YTMusic

router = APIRouter()
logger = logging.getLogger(__name__)


def handle_podcast_errors(operation_name: str, identifier: str):
    """Helper function to handle common podcast-related errors"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)

            except KeyError as e:
                logger.error(f"KeyError in {operation_name} for {identifier}: {str(e)}")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "API structure error",
                        "message": f"YouTube Music API structure has changed, {operation_name.replace('_', ' ')} temporarily unavailable",
                        "identifier": identifier,
                        "technical_details": str(e),
                    },
                )

            except Exception as e:
                logger.error(f"Unexpected error in {operation_name} for {identifier}: {str(e)}")
                if "not found" in str(e).lower() or "unavailable" in str(e).lower():
                    raise HTTPException(
                        status_code=404,
                        detail=f"{operation_name.replace('_', ' ').title()} with ID {identifier} not found or unavailable",
                    )
                elif "auth" in str(e).lower():
                    raise HTTPException(
                        status_code=401,
                        detail=f"Authentication required to access {operation_name.replace('_', ' ')}",
                    )

                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Internal server error",
                        "message": f"An unexpected error occurred while fetching {operation_name.replace('_', ' ')}",
                        "identifier": identifier,
                    },
                )

        return wrapper

    return decorator


@router.get("/channel/{channelId}")
async def get_channel(channelId: str):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_channel(channelId)

        if not results:
            raise HTTPException(status_code=404, detail="Channel not found")

        return {"message": "OK", "query": channelId, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_channel for {channelId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, channel data temporarily unavailable",
                "channelId": channelId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_channel for {channelId}: {str(e)}")
        if "not found" in str(e).lower() or "unavailable" in str(e).lower():
            raise HTTPException(
                status_code=404, detail=f"Channel with ID {channelId} not found or unavailable"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching channel data",
                "channelId": channelId,
            },
        )


@router.get("/channel_episodes/{channelId}")
async def get_channel_episodes(channelId: str, params: str):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_channel_episodes(channelId, params)

        if not results:
            raise HTTPException(status_code=404, detail="Channel episodes not found")

        return {"message": "OK", "query": channelId, "params": params, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_channel_episodes for {channelId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, channel episodes temporarily unavailable",
                "channelId": channelId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_channel_episodes for {channelId}: {str(e)}")
        if "not found" in str(e).lower() or "unavailable" in str(e).lower():
            raise HTTPException(
                status_code=404, detail=f"Channel episodes for {channelId} not found or unavailable"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching channel episodes",
                "channelId": channelId,
            },
        )


@router.get("/podcast/{playlistId}")
@handle_podcast_errors("get_podcast", "playlistId")
async def get_podcast(playlistId: str, limit: int | None = 100):
    ytmusic = YTMusic()
    results = ytmusic.get_podcast(playlistId, limit)

    if not results:
        raise HTTPException(status_code=404, detail="Podcast not found")

    return {"message": "OK", "query": playlistId, "result": results}


@router.get("/episode/{videoId}")
@handle_podcast_errors("get_episode", "videoId")
async def get_episode(videoId: str):
    ytmusic = YTMusic()
    results = ytmusic.get_episode(videoId)

    if not results:
        raise HTTPException(status_code=404, detail="Episode not found")

    return {"message": "OK", "query": videoId, "result": results}


@router.get("/episodes_playlist/{playlist_id}")
@handle_podcast_errors("get_episodes_playlist", "playlist_id")
async def get_episodes_playlist(playlist_id: str = "RDPN"):
    ytmusic = YTMusic()
    results = ytmusic.get_episodes_playlist(playlist_id)

    if not results:
        raise HTTPException(status_code=404, detail="Episodes playlist not found")

    return {"message": "OK", "query": playlist_id, "result": results}
