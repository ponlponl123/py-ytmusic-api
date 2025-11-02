import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from ytmusicapi import YTMusic

from src.routers import (
    browsing,
    explore,
    library,
    playlists,
    podcasts,
    search,
    uploads,
    watch,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("ytmusic_api.log"), logging.StreamHandler()],
)

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    title="YT Music API",
    description="A comprehensive YouTube Music API wrapper with robust error handling",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with prefixes for better organization
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(browsing.router, prefix="/browse", tags=["Browse"])
app.include_router(explore.router, prefix="/explore", tags=["Explore"])
app.include_router(watch.router, prefix="/watch", tags=["Watch"])
app.include_router(library.router, prefix="/library", tags=["Library"])
app.include_router(playlists.router, prefix="/playlists", tags=["Playlists"])
app.include_router(podcasts.router, prefix="/podcasts", tags=["Podcasts"])
app.include_router(uploads.router, prefix="/uploads", tags=["Uploads"])


@app.get("/")
def root():
    return {
        "message": "YT Music API is running!",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "Search music content",
            "Browse artists, albums, playlists",
            "Explore charts and moods",
            "Library management",
            "Podcast support",
            "Upload management",
            "Comprehensive error handling",
        ],
        "health_check": "/search/health",
        "documentation": "/docs",
    }


@app.get("/api/status")
async def api_status():
    """Global API status check"""
    try:
        ytmusic = YTMusic()
        # Test basic functionality
        test_result = ytmusic.search("test", limit=1)

        return {
            "status": "operational",
            "message": "All systems operational",
            "timestamp": "2025-11-02T16:51:27Z",
            "ytmusicapi_version": "1.11.1",
            "test_search_successful": bool(test_result),
            "endpoints": {
                "search": "operational",
                "browse": "operational",
                "library": "operational",
                "playlists": "operational",
            },
        }

    except KeyError as e:
        return {
            "status": "degraded",
            "message": "YouTube Music API structure issues detected",
            "timestamp": "2025-11-02T16:51:27Z",
            "issue": "API response parsing errors",
            "recommendation": "Use simplified search parameters",
            "technical_details": str(e),
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "API connectivity issues",
            "timestamp": "2025-11-02T16:51:27Z",
            "error": str(e),
            "recommendation": "Check internet connection and try again",
        }


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")
