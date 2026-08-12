import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from ytmusicapi import YTMusic

from src.utils.cache import build_cache_key, execute_ytmusic_call
from src.utils.client import get_request_auth_key, get_request_user_lang, get_ytmusic
from src.utils.error_handlers import handle_browse_errors

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
@router.get("/explore")
@handle_browse_errors
async def get_explore(
    request: Request, ytmusic: YTMusic = Depends(get_ytmusic)
):
    """Retrieves main YouTube Music explore page content."""
    auth_key = get_request_auth_key(request)
    lang = get_request_user_lang(request)
    cache_key = build_cache_key("explore:main", auth_key, lang=lang)
    results = await execute_ytmusic_call(ytmusic.get_explore, cache_key=cache_key)

    if not results:
        raise HTTPException(status_code=404, detail="Explore content not found")

    return {"message": "OK", "result": results}


@router.get("/mood_playlists/{query}")
@handle_browse_errors
async def get_mood_playlists(
    query: str, request: Request, ytmusic: YTMusic = Depends(get_ytmusic)
):
    auth_key = get_request_auth_key(request)
    lang = get_request_user_lang(request)
    cache_key = build_cache_key("explore:mood", auth_key, query, lang=lang)
    results = await execute_ytmusic_call(
        ytmusic.get_mood_playlists, query, cache_key=cache_key
    )

    if not results:
        raise HTTPException(status_code=404, detail="No mood playlists found for this query")

    return {"message": "OK", "query": query, "result": results}


@router.get("/charts/{country}")
@handle_browse_errors
async def get_charts(
    request: Request, country: str = "ZZ", ytmusic: YTMusic = Depends(get_ytmusic)
):
    auth_key = get_request_auth_key(request)
    lang = get_request_user_lang(request)
    cache_key = build_cache_key("explore:charts", auth_key, country, lang=lang)
    results = await execute_ytmusic_call(
        ytmusic.get_charts, country, cache_key=cache_key
    )

    if not results:
        raise HTTPException(status_code=404, detail=f"No charts found for country: {country}")

    return {"message": "OK", "query": country, "result": results}
