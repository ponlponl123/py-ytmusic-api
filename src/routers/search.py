import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from ytmusicapi import YTMusic

router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    """Health check endpoint to test basic YTMusic API functionality"""
    try:
        ytmusic = YTMusic()
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


@router.get("/search")
async def search(
    query: str = Query(..., description="Search query"),
    filter: str | None = None,
    ignore_spelling: bool = False,
    limit: int = 20,
    scope: str | None = None,
):
    try:
        ytmusic = YTMusic()
        search_results = ytmusic.search(
            query=query, filter=filter, ignore_spelling=ignore_spelling, limit=limit, scope=scope
        )

        if not search_results:
            raise HTTPException(status_code=404, detail="No search result found")

        return {"message": "OK", "query": query, "result": search_results}

    except KeyError as e:
        # Handle YouTube Music API structure changes
        logger.error(f"KeyError in search API: {str(e)}")

        # Try search without problematic parameters that might cause parsing issues
        try:
            ytmusic = YTMusic()
            # Simplified search without scope parameter which might cause issues
            simplified_results = ytmusic.search(
                query=query,
                filter=filter,
                limit=min(limit, 10),  # Reduce limit to avoid complex results
            )

            if simplified_results:
                return {
                    "message": "OK (simplified results due to API changes)",
                    "query": query,
                    "result": simplified_results,
                    "warning": "Some advanced search features may be temporarily unavailable",
                }
        except Exception as fallback_error:
            logger.error(f"Fallback search also failed: {str(fallback_error)}")

        # Return error with helpful message
        raise HTTPException(
            status_code=503,
            detail={
                "error": "YouTube Music API structure has changed",
                "message": "The search service is temporarily experiencing issues due to YouTube Music API changes. Please try again later or contact support.",
                "query": query,
                "technical_details": str(e) if "header" in str(e) else "API parsing error",
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while processing your search request",
                "query": query,
            },
        )


@router.get("/search_suggestions")
async def get_search_suggestions(
    query: str = Query(..., description="Search query"), detailed_runs: bool = False
):
    try:
        ytmusic = YTMusic()
        search_results = ytmusic.get_search_suggestions(query=query, detailed_runs=detailed_runs)

        if not search_results:
            raise HTTPException(status_code=404, detail="No search result found")

        return {"message": "OK", "query": query, "result": search_results}

    except KeyError as e:
        logger.error(f"KeyError in search suggestions API: {str(e)}")

        # Try without detailed_runs if that's causing issues
        try:
            ytmusic = YTMusic()
            simplified_results = ytmusic.get_search_suggestions(query=query, detailed_runs=False)

            if simplified_results:
                return {
                    "message": "OK (simplified suggestions)",
                    "query": query,
                    "result": simplified_results,
                    "warning": "Detailed search suggestions temporarily unavailable",
                }
        except Exception:
            pass

        raise HTTPException(
            status_code=503,
            detail={
                "error": "Search suggestions API error",
                "message": "Search suggestions are temporarily unavailable due to API changes",
                "query": query,
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in search suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while getting search suggestions",
                "query": query,
            },
        )


@router.delete("/search_suggestions")
async def remove_search_suggestions(
    suggestions: list[dict[str, Any]], indices: list[int] | None = None
):
    try:
        ytmusic = YTMusic()
        results = ytmusic.remove_search_suggestions(suggestions=suggestions, indices=indices)

        return {"message": "OK", "query": suggestions, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in remove search suggestions API: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Remove suggestions API error",
                "message": "Cannot remove search suggestions due to API changes",
                "suggestions": suggestions,
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in remove search suggestions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while removing search suggestions",
                "suggestions": suggestions,
            },
        )
