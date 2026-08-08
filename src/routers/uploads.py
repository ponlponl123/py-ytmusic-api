import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from ytmusicapi import YTMusic

from src.utils.cache import execute_ytmusic_call
from src.utils.client import get_ytmusic
from src.utils.error_handlers import handle_upload_errors

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/library_upload_songs")
@handle_upload_errors
async def get_library_upload_songs(
    limit: int | None = 25,
    order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    results = await execute_ytmusic_call(ytmusic.get_library_upload_songs, limit, order=order)

    return {"message": "OK", "result": results}


@router.get("/library_upload_artists")
@handle_upload_errors
async def get_library_upload_artists(
    limit: int | None = 25,
    order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    results = await execute_ytmusic_call(ytmusic.get_library_upload_artists, limit, order=order)

    return {"message": "OK", "result": results}


@router.get("/library_upload_albums")
@handle_upload_errors
async def get_library_upload_albums(
    limit: int | None = 25,
    order: Literal["a_to_z", "z_to_a", "recently_added"] | None = None,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    results = await execute_ytmusic_call(ytmusic.get_library_upload_albums, limit, order=order)

    return {"message": "OK", "result": results}


@router.get("/library_upload_artist/{browseId}")
@handle_upload_errors
async def get_library_upload_artist(
    browseId: str, limit: int = 25, ytmusic: YTMusic = Depends(get_ytmusic)
):
    results = await execute_ytmusic_call(ytmusic.get_library_upload_artist, browseId, limit)

    if not results:
        raise HTTPException(status_code=404, detail=f"Upload artist with ID {browseId} not found")

    return {"message": "OK", "browseId": browseId, "result": results}


@router.get("/library_upload_album/{browseId}")
@handle_upload_errors
async def get_library_upload_album(
    browseId: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
    results = await execute_ytmusic_call(ytmusic.get_library_upload_album, browseId)

    if not results:
        raise HTTPException(status_code=404, detail=f"Upload album with ID {browseId} not found")

    return {"message": "OK", "browseId": browseId, "result": results}


@router.post("/upload_song/{filepath}")
@handle_upload_errors
async def upload_song(
    filepath: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
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

    results = await execute_ytmusic_call(ytmusic.upload_song, filepath)

    return {"message": "OK", "filepath": filepath, "result": results}


@router.delete("/upload_entity/{entityId}")
@handle_upload_errors
async def delete_upload_entity(
    entityId: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
    if not entityId.strip():
        raise HTTPException(status_code=400, detail="Entity ID cannot be empty")

    results = await execute_ytmusic_call(ytmusic.delete_upload_entity, entityId)

    return {"message": "OK", "entityId": entityId, "result": results}
