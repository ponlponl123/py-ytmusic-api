import logging
import sys
import traceback
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import JSONResponse
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

# Configure logging with more comprehensive settings
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ytmusic_api.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ],
)

# Get logger for the main application
logger = logging.getLogger(__name__)

# Log startup
logger.info("=" * 80)
logger.info("YT Music API Starting Up")
logger.info(f"Startup Time: {datetime.now().isoformat()}")
logger.info("=" * 80)

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


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and responses"""
    start_time = datetime.now()
    
    # Log incoming request
    logger.info(
        f"Incoming Request: {request.method} {request.url.path} | "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        
        # Calculate request duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Log response
        logger.info(
            f"Response: {response.status_code} | "
            f"Path: {request.url.path} | "
            f"Duration: {duration:.3f}s"
        )
        
        return response
    except Exception as e:
        # Log any errors that occur during request processing
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(
            f"Request Failed: {request.method} {request.url.path} | "
            f"Error: {type(e).__name__}: {str(e)} | "
            f"Duration: {duration:.3f}s"
        )
        raise


# Global exception handlers to log all errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Log all HTTP exceptions"""
    # Use INFO for client errors (4xx), ERROR for server errors (5xx)
    log_level = logging.INFO if 400 <= exc.status_code < 500 else logging.ERROR
    logger.log(
        log_level,
        f"HTTP Exception: {exc.status_code} - {exc.detail} | "
        f"Path: {request.url.path} | Method: {request.method} | "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log all validation errors"""
    # Use INFO for validation errors (client-side errors)
    logger.info(
        f"Validation Error: {exc.errors()} | "
        f"Path: {request.url.path} | Method: {request.method} | "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Log all uncaught exceptions"""
    error_traceback = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(
        f"Uncaught Exception: {type(exc).__name__}: {str(exc)} | "
        f"Path: {request.url.path} | Method: {request.method} | "
        f"Client: {request.client.host if request.client else 'unknown'}\n"
        f"Traceback:\n{error_traceback}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "type": type(exc).__name__
            }
        }
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


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    logger.info("=" * 80)
    logger.info("YT Music API Shutting Down")
    logger.info(f"Shutdown Time: {datetime.now().isoformat()}")
    logger.info("=" * 80)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0")
