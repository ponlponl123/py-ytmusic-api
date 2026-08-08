import logging

import logging

from fastapi import APIRouter, Depends, HTTPException
from ytmusicapi import YTMusic

from src.utils.client import get_ytmusic
from src.utils.error_handlers import handle_browse_errors

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/mood_playlists/{query}")
@handle_browse_errors
async def get_mood_playlists(
    query: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
    results = ytmusic.get_mood_playlists(query)

    if not results:
        raise HTTPException(status_code=404, detail="No mood playlists found for this query")

    return {"message": "OK", "query": query, "result": results}


@router.get("/charts/{country}")
@handle_browse_errors
async def get_charts(
    country: str = "ZZ", ytmusic: YTMusic = Depends(get_ytmusic)
):
    results = ytmusic.get_charts(country)

    if not results:
        raise HTTPException(status_code=404, detail=f"No charts found for country: {country}")

    return {"message": "OK", "query": country, "result": results}

