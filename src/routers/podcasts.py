import logging

import logging

from fastapi import APIRouter, Depends, HTTPException
from ytmusicapi import YTMusic

from src.utils.client import get_ytmusic
from src.utils.error_handlers import handle_browse_errors

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/channel/{channelId}")
@handle_browse_errors
async def get_channel(
    channelId: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
    results = ytmusic.get_channel(channelId)

    if not results:
        raise HTTPException(status_code=404, detail="Channel not found")

    return {"message": "OK", "query": channelId, "result": results}


@router.get("/channel_episodes/{channelId}")
@handle_browse_errors
async def get_channel_episodes(
    channelId: str, params: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
    results = ytmusic.get_channel_episodes(channelId, params)

    if not results:
        raise HTTPException(status_code=404, detail="Channel episodes not found")

    return {"message": "OK", "query": channelId, "params": params, "result": results}


@router.get("/podcast/{playlistId}")
@handle_browse_errors
async def get_podcast(
    playlistId: str,
    limit: int | None = 100,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    results = ytmusic.get_podcast(playlistId, limit)

    if not results:
        raise HTTPException(status_code=404, detail="Podcast not found")

    return {"message": "OK", "query": playlistId, "result": results}


@router.get("/episode/{videoId}")
@handle_browse_errors
async def get_episode(
    videoId: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
    results = ytmusic.get_episode(videoId)

    if not results:
        raise HTTPException(status_code=404, detail="Episode not found")

    return {"message": "OK", "query": videoId, "result": results}


@router.get("/episodes_playlist/{playlist_id}")
@handle_browse_errors
async def get_episodes_playlist(
    playlist_id: str = "RDPN", ytmusic: YTMusic = Depends(get_ytmusic)
):
    results = ytmusic.get_episodes_playlist(playlist_id)

    if not results:
        raise HTTPException(status_code=404, detail="Episodes playlist not found")

    return {"message": "OK", "query": playlist_id, "result": results}

