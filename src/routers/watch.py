import logging

from fastapi import APIRouter, HTTPException
from ytmusicapi import YTMusic

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/mood_categories")
def get_mood_categories():
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_mood_categories()

        return {"message": "OK", "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_mood_categories: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, mood categories temporarily unavailable",
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_mood_categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching mood categories",
            },
        )


@router.get("/watch/{videoId}")
async def get_watch_playlist(
    videoId: str,
    playlistId: str | None = None,
    limit: int = 25,
    radio: bool = False,
    shuffle: bool = False,
):
    try:
        # Validate limit
        if limit < 1:
            raise HTTPException(status_code=400, detail="Limit must be greater than 0")
        if limit > 100:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 100")

        ytmusic = YTMusic()
        results = ytmusic.get_watch_playlist(
            videoId=videoId, playlistId=playlistId, limit=limit, radio=radio, shuffle=shuffle
        )

        if not results:
            raise HTTPException(status_code=404, detail="Video not found")

        return {"message": "OK", "videoId": videoId, "playlistId": playlistId, "result": results}

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in get_watch_playlist for {videoId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, watch playlist temporarily unavailable",
                "videoId": videoId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_watch_playlist for {videoId}: {str(e)}")
        if "not found" in str(e).lower() or "unavailable" in str(e).lower():
            raise HTTPException(
                status_code=404, detail=f"Video with ID {videoId} not found or unavailable"
            )
        elif "invalid" in str(e).lower():
            raise HTTPException(status_code=400, detail=f"Invalid video ID: {videoId}")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching watch playlist",
                "videoId": videoId,
            },
        )
