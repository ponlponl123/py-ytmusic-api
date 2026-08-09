import logging
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from ytmusicapi import YTMusic

from src.utils.cache import execute_ytmusic_call
from src.utils.client import get_ytmusic
from src.utils.error_handlers import handle_search_errors

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check(ytmusic: YTMusic = Depends(get_ytmusic)):
    """Health check endpoint to test basic YTMusic API functionality"""
    try:
        test_results = await execute_ytmusic_call(ytmusic.search, "test", limit=1)

        return {
            "status": "healthy",
            "message": "YTMusic API is working correctly",
            "ytmusicapi_working": True,
            "test_search_successful": bool(test_results),
        }

    except KeyError as e:
        return {
            "status": "degraded",
            "message": "YTMusic API has structure issues but may still work for simple queries",
            "ytmusicapi_working": False,
            "error_type": "KeyError",
            "error_details": str(e),
            "recommendation": "Use simplified search parameters",
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "message": "YTMusic API is not working",
            "ytmusicapi_working": False,
            "error_type": type(e).__name__,
            "error_details": str(e),
            "recommendation": "Check internet connection and try again later",
        }


import re

DUMMY_KEYWORDS = {"song", "video", "album", "playlist", "podcast", "episode", "artist", "single", "music", "result", "track"}

def _enrich_search_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Enrich search results by adding category labels based on resultType,
    cleaning dummy artist names, and extracting missing duration timestamps.
    """
    category_map = {
        "song": "Songs",
        "video": "Videos",
        "artist": "Artists",
        "album": "Albums",
        "playlist": "Playlists",
        "episode": "Episodes",
        "podcast": "Podcasts",
        "profile": "Profiles",
    }

    enriched_results = []
    for item in results:
        enriched_item = item.copy()
        if enriched_item.get("category") is None and "resultType" in enriched_item:
            result_type = enriched_item["resultType"]
            enriched_item["category"] = category_map.get(result_type, None)

        # 1. Clean & enrich artists array
        artists = enriched_item.get("artists")
        valid_artists = []
        if isinstance(artists, list):
            for a in artists:
                name = a.get("name") if isinstance(a, dict) else (a if isinstance(a, str) else None)
                if name:
                    clean = re.sub(r"\s*-\s*Topic\s*$", "", name, flags=re.IGNORECASE).strip()
                    if clean.lower() not in DUMMY_KEYWORDS and not re.match(r"^\d{1,2}:\d{2}(?::\d{2})?$", clean):
                        valid_artists.append({"name": clean, "id": a.get("id") if isinstance(a, dict) else None})

        if not valid_artists:
            # Try author / channel / uploader / title
            author = enriched_item.get("author") or enriched_item.get("channel") or enriched_item.get("uploader")
            if isinstance(author, str):
                clean_auth = re.sub(r"\s*-\s*Topic\s*$", "", author, flags=re.IGNORECASE).strip()
                if clean_auth and clean_auth.lower() not in DUMMY_KEYWORDS:
                    valid_artists.append({"name": clean_auth, "id": enriched_item.get("artistId")})

        if not valid_artists and enriched_item.get("title"):
            title = str(enriched_item["title"])
            feat_match = re.search(r"(?:feat\.|ft\.|featuring)\s*@?([^\)\],|]+)", title, re.IGNORECASE)
            if feat_match:
                for part in re.split(r"&|,", feat_match.group(1)):
                    clean_part = part.strip()
                    if clean_part and clean_part.lower() not in DUMMY_KEYWORDS:
                        valid_artists.append({"name": clean_part, "id": None})

            dash_match = re.search(r"^([^-]+)\s*-\s*", title)
            if dash_match and not valid_artists:
                clean_dash = dash_match.group(1).strip()
                if len(clean_dash) > 1 and not clean_dash.isdigit() and clean_dash.lower() not in DUMMY_KEYWORDS:
                    valid_artists.append({"name": clean_dash, "id": None})

        if valid_artists:
            enriched_item["artists"] = valid_artists

        # 2. Extract missing duration
        if not enriched_item.get("duration") and not enriched_item.get("duration_seconds"):
            sources = [
                enriched_item.get("lengthText"),
                enriched_item.get("length"),
                enriched_item.get("subtitle"),
                enriched_item.get("byline"),
            ]
            for src in sources:
                if isinstance(src, str):
                    ts_match = re.search(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", src)
                    if ts_match:
                        enriched_item["duration"] = ts_match.group(0)
                        break

        enriched_results.append(enriched_item)

    return enriched_results


SearchFilter = Literal[
    "songs",
    "videos",
    "albums",
    "artists",
    "playlists",
    "community_playlists",
    "featured_playlists",
    "profiles",
    "podcasts",
    "episodes",
]


@router.get("/")
@handle_search_errors
# pylint: disable=redefined-builtin, too-many-positional-arguments
async def search(
    query: str = Query(..., description="Search query"),
    filter: SearchFilter | None = Query(None, description="Optional search filter"),
    ignore_spelling: bool = False,
    limit: int = 20,
    scope: Literal["uploads", "library"] | None = Query(None, description="Optional search scope"),
    enrich_categories: bool = True,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    try:
        search_results = await execute_ytmusic_call(
            ytmusic.search,
            query=query,
            filter=filter,
            ignore_spelling=ignore_spelling,
            limit=limit,
            scope=scope,
        )
    except KeyError as e:
        logger.warning("Search failed with KeyError, trying simplified fallback: %s", e)
        try:
            simplified_results = await execute_ytmusic_call(
                ytmusic.search,
                query=query,
                filter=filter,
                limit=min(limit, 10),
            )
            if simplified_results:
                return {
                    "message": "OK (simplified results due to API changes)",
                    "query": query,
                    "result": simplified_results,
                    "warning": "Some advanced search features may be temporarily unavailable",
                }
        except Exception as fallback_error:
            logger.error("Fallback search also failed: %s", fallback_error)
        raise e

    if not search_results:
        raise HTTPException(status_code=404, detail="No search result found")

    if enrich_categories:
        search_results = _enrich_search_results(search_results)

    return {"message": "OK", "query": query, "result": search_results}


@router.get("/suggestions")
@handle_search_errors
async def get_suggestions(
    query: str = Query(..., description="Search query"),
    detailed_runs: bool = False,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    try:
        search_results = await execute_ytmusic_call(
            ytmusic.get_search_suggestions, query=query, detailed_runs=detailed_runs
        )
    except KeyError as e:
        if detailed_runs:
            logger.warning("Suggestions with detailed_runs failed, trying simplified: %s", e)
            try:
                simplified_results = await execute_ytmusic_call(
                    ytmusic.get_search_suggestions, query=query, detailed_runs=False
                )
                if simplified_results:
                    return {
                        "message": "OK (simplified suggestions)",
                        "query": query,
                        "result": simplified_results,
                        "warning": "Detailed search suggestions temporarily unavailable",
                    }
            except Exception:
                pass
        raise e

    if not search_results:
        raise HTTPException(status_code=404, detail="No search result found")

    return {"message": "OK", "query": query, "result": search_results}


@router.delete("/suggestions")
@handle_search_errors
async def remove_suggestions(
    suggestions: list[dict[str, Any]],
    indices: list[int] | None = None,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    results = await execute_ytmusic_call(
        ytmusic.remove_search_suggestions, suggestions=suggestions, indices=indices
    )
    return {"message": "OK", "query": suggestions, "result": results}
