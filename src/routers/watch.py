import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from ytmusicapi import YTMusic

from src.utils.cache import execute_ytmusic_call
from src.utils.client import get_request_auth_key, get_ytmusic
from src.utils.error_handlers import handle_browse_errors

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/mood_categories")
@handle_browse_errors
async def get_mood_categories(
    request: Request, ytmusic: YTMusic = Depends(get_ytmusic)
):
    auth_key = get_request_auth_key(request)
    cache_key = "watch:mood_categories" if not auth_key else None
    results = await execute_ytmusic_call(
        ytmusic.get_mood_categories, cache_key=cache_key
    )
    return {"message": "OK", "result": results}


@router.get("/signature_timestamp")
@handle_browse_errors
async def get_signature_timestamp(
    url: str | None = None, ytmusic: YTMusic = Depends(get_ytmusic)
):
    """Retrieves YouTube player signature timestamp for audio token decryption."""
    results = await execute_ytmusic_call(ytmusic.get_signatureTimestamp, url=url)
    return {"message": "OK", "result": results}


@router.get("/playlist/{videoId}")
@handle_browse_errors
async def get_watch_playlist(
    videoId: str,
    playlistId: str | None = None,
    limit: int = 25,
    radio: bool = False,
    shuffle: bool = False,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    # Validate limit
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0")
    if limit > 100:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 100")

    results = await execute_ytmusic_call(
        ytmusic.get_watch_playlist,
        videoId=videoId,
        playlistId=playlistId,
        limit=limit,
        radio=radio,
        shuffle=shuffle,
    )

    if not results:
        raise HTTPException(status_code=404, detail="Video not found")

    return {"message": "OK", "videoId": videoId, "playlistId": playlistId, "result": results}
