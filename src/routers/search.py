import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from src.utils.client import YTMusicClient
from src.utils.error_handlers import handle_search_errors

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """Health check endpoint to test basic YTMusic API functionality"""
    try:
        ytmusic = YTMusicClient.get_client()
        # Try a simple search to test API connectivity
        test_results = ytmusic.search("test", limit=1)

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


def _enrich_search_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Enrich search results by adding category labels based on resultType
    when category is null (common when filter is None or "all").
    """
    # Category mapping based on resultType
    category_map = {
        "song": "Songs",
        "video": "Videos",
        "artist": "Artists",
        "album": "Albums",
        "playlist": "Playlists",
        "episode": "Episodes",
    }

    enriched_results = []
    for item in results:
        # Create a copy to avoid modifying the original
        enriched_item = item.copy()

        # If category is null and we have a resultType, infer the category
        if enriched_item.get("category") is None and "resultType" in enriched_item:
            result_type = enriched_item["resultType"]
            enriched_item["category"] = category_map.get(result_type, None)

        enriched_results.append(enriched_item)

    return enriched_results


@router.get("/")
@handle_search_errors
# pylint: disable=redefined-builtin, too-many-positional-arguments
async def search(
    query: str = Query(..., description="Search query"),
    filter: str | None = None,
    ignore_spelling: bool = False,
    limit: int = 20,
    scope: str | None = None,
    enrich_categories: bool = True,
):
    ytmusic = YTMusicClient.get_client()
    try:
        search_results = ytmusic.search(
            query=query, filter=filter, ignore_spelling=ignore_spelling, limit=limit, scope=scope
        )
    except KeyError as e:
        logger.warning("Search failed with KeyError, trying simplified fallback: %s", e)
        try:
            # Simplified search without scope parameter to avoid parsing issues
            simplified_results = ytmusic.search(
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
    query: str = Query(..., description="Search query"), detailed_runs: bool = False
):
    ytmusic = YTMusicClient.get_client()
    try:
        search_results = ytmusic.get_search_suggestions(query=query, detailed_runs=detailed_runs)
    except KeyError as e:
        if detailed_runs:
            logger.warning("Suggestions with detailed_runs failed, trying simplified: %s", e)
            try:
                simplified_results = ytmusic.get_search_suggestions(
                    query=query, detailed_runs=False
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
async def remove_suggestions(suggestions: list[dict[str, Any]], indices: list[int] | None = None):
    ytmusic = YTMusicClient.get_client()
    results = ytmusic.remove_search_suggestions(suggestions=suggestions, indices=indices)
    return {"message": "OK", "query": suggestions, "result": results}
