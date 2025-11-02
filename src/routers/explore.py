import logging

from fastapi import APIRouter, HTTPException
from ytmusicapi import YTMusic

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/mood_playlists/{query}")
async def get_mood_playlists(query: str):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_mood_playlists(query)

        if not results:
            raise HTTPException(status_code=404, detail="No mood playlists found for this query")

        return {"message": "OK", "query": query, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_mood_playlists for {query}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, mood playlists temporarily unavailable",
                "query": query,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_mood_playlists for {query}: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"No mood playlists found for '{query}'")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching mood playlists",
                "query": query,
            },
        )


@router.get("/charts/{country}")
async def get_charts(country: str = "ZZ"):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_charts(country)

        if not results:
            raise HTTPException(status_code=404, detail=f"No charts found for country: {country}")

        return {"message": "OK", "query": country, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_charts for {country}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, charts temporarily unavailable",
                "country": country,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_charts for {country}: {str(e)}")
        if "invalid" in str(e).lower() or "not supported" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid country code: {country}. Please use a valid ISO country code.",
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching charts",
                "country": country,
            },
        )
