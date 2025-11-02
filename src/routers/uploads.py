import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from ytmusicapi import YTMusic

router = APIRouter()
logger = logging.getLogger(__name__)


def handle_upload_errors(operation_name: str):
    """Helper function to handle common upload-related errors"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)

            except KeyError as e:
                logger.error(f"KeyError in {operation_name}: {str(e)}")
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "API structure error",
                        "message": f"YouTube Music API structure has changed, {operation_name.replace('_', ' ')} temporarily unavailable",
                        "technical_details": str(e),
                    },
                )

            except Exception as e:
                logger.error(f"Unexpected error in {operation_name}: {str(e)}")
                if "auth" in str(e).lower() or "login" in str(e).lower():
                    raise HTTPException(
                        status_code=401,
                        detail=f"Authentication required to access {operation_name.replace('_', ' ')}",
                    )
                elif "not found" in str(e).lower():
                    raise HTTPException(
                        status_code=404,
                        detail=f"{operation_name.replace('_', ' ').title()} not found",
                    )

                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Internal server error",
                        "message": f"An unexpected error occurred while {operation_name.replace('_', ' ')}",
                    },
                )

        return wrapper

    return decorator


@router.get("/library_upload_songs")
@handle_upload_errors("get_library_upload_songs")
async def get_library_upload_songs(
    limit: int | None = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusic()
    results = ytmusic.get_library_upload_songs(limit, order=order)

    return {"message": "OK", "result": results}


@router.get("/library_upload_artists")
@handle_upload_errors("get_library_upload_artists")
async def get_library_upload_artists(
    limit: int | None = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusic()
    results = ytmusic.get_library_upload_artists(limit, order=order)

    return {"message": "OK", "result": results}


@router.get("/library_upload_albums")
@handle_upload_errors("get_library_upload_albums")
async def get_library_upload_albums(
    limit: int | None = 25, order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None
):
    ytmusic = YTMusic()
    results = ytmusic.get_library_upload_albums(limit, order=order)

    return {"message": "OK", "result": results}


@router.get("/library_upload_artist/{browseId}")
@handle_upload_errors("get_library_upload_artist")
async def get_library_upload_artist(browseId: str, limit: int = 25):
    ytmusic = YTMusic()
    results = ytmusic.get_library_upload_artist(browseId, limit)

    if not results:
        raise HTTPException(status_code=404, detail=f"Upload artist with ID {browseId} not found")

    return {"message": "OK", "browseId": browseId, "result": results}


@router.get("/library_upload_album/{browseId}")
@handle_upload_errors("get_library_upload_album")
async def get_library_upload_album(browseId: str):
    ytmusic = YTMusic()
    results = ytmusic.get_library_upload_album(browseId)

    if not results:
        raise HTTPException(status_code=404, detail=f"Upload album with ID {browseId} not found")

    return {"message": "OK", "browseId": browseId, "result": results}


@router.post("/upload_song/{filepath}")
async def upload_song(filepath: str):
    try:
        # Basic validation
        if not filepath.strip():
            raise HTTPException(status_code=400, detail="Filepath cannot be empty")

        # Check if filepath has a valid audio extension
        valid_extensions = [".mp3", ".flac", ".m4a", ".wav", ".ogg", ".aac"]
        if not any(filepath.lower().endswith(ext) for ext in valid_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension. Supported formats: {', '.join(valid_extensions)}",
            )

        ytmusic = YTMusic()
        results = ytmusic.upload_song(filepath)

        return {"message": "OK", "filepath": filepath, "result": results}

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in upload_song for {filepath}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot upload song",
                "filepath": filepath,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in upload_song for {filepath}: {str(e)}")
        if "auth" in str(e).lower() or "login" in str(e).lower():
            raise HTTPException(status_code=401, detail="Authentication required to upload songs")
        elif "file not found" in str(e).lower() or "no such file" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"File not found: {filepath}")
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            raise HTTPException(
                status_code=429, detail="Upload quota exceeded or rate limit reached"
            )
        elif "format" in str(e).lower() or "unsupported" in str(e).lower():
            raise HTTPException(
                status_code=400, detail=f"Unsupported file format or corrupted file: {filepath}"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while uploading song",
                "filepath": filepath,
            },
        )


@router.delete("/upload_entity/{entityId}")
async def delete_upload_entity(entityId: str):
    try:
        if not entityId.strip():
            raise HTTPException(status_code=400, detail="Entity ID cannot be empty")

        ytmusic = YTMusic()
        results = ytmusic.delete_upload_entity(entityId)

        return {"message": "OK", "entityId": entityId, "result": results}

    except HTTPException:
        raise  # Re-raise HTTP exceptions

    except KeyError as e:
        logger.error(f"KeyError in delete_upload_entity for {entityId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot delete upload entity",
                "entityId": entityId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in delete_upload_entity for {entityId}: {str(e)}")
        if "auth" in str(e).lower() or "login" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to delete upload entities"
            )
        elif "not found" in str(e).lower():
            raise HTTPException(
                status_code=404, detail=f"Upload entity with ID {entityId} not found"
            )
        elif "permission" in str(e).lower():
            raise HTTPException(
                status_code=403, detail="You don't have permission to delete this upload entity"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while deleting upload entity",
                "entityId": entityId,
            },
        )
