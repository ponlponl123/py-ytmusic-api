import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from ytmusicapi import YTMusic

from src.utils.cache import execute_ytmusic_call
from src.utils.client import get_ytmusic
from src.utils.error_handlers import handle_browse_errors

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/home")
@handle_browse_errors
async def get_home(limit: int = 3, ytmusic: YTMusic = Depends(get_ytmusic)):
    search_results = await execute_ytmusic_call(ytmusic.get_home, limit)

    if not search_results:
        raise HTTPException(status_code=404, detail="No home content found")

    return {"message": "OK", "limit": limit, "result": search_results}



@router.get("/artist/{channelId}")
@handle_browse_errors
async def get_artist(channelId: str, ytmusic: YTMusic = Depends(get_ytmusic)):
    # Perform ID validation first to prevent unnecessary requests or handle errors gracefully
    if channelId.startswith("VL") or channelId.startswith("OLAK") or channelId.startswith("PL"):
        logger.info("Client attempted to use playlist/album ID '%s' on artist endpoint", channelId)
        if channelId.startswith("VL"):
            clean_id = channelId[2:]
            recommendation = f"Use /playlists/{clean_id} for playlists"
        elif channelId.startswith("OLAK"):
            recommendation = f"Use /playlists/{channelId} or /browse/album/{channelId} for albums"
        else:
            recommendation = f"Use /playlists/{channelId} for playlists"
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid ID type",
                "message": "This appears to be a playlist or album ID, not an artist/channel ID",
                "channelId": channelId,
                "recommendation": recommendation,
            },
        )

    try:
        search_results = ytmusic.get_artist(channelId)
    except KeyError as artist_error:
        error_str = str(artist_error)
        if "musicImmersiveHeaderRenderer" in error_str or "musicVisualHeaderRenderer" in error_str:
            logger.info(
                "get_artist failed for %s due to header renderer issue (%s), "
                "trying get_user fallback",
                channelId,
                error_str,
            )
            try:
                search_results = ytmusic.get_user(channelId)
                logger.info("get_user fallback successful for %s", channelId)
                return {
                    "message": "OK",
                    "query": channelId,
                    "result": search_results,
                    "note": "Retrieved using user endpoint due to API structure differences",
                }
            except Exception as user_error:
                logger.error(
                    "Both get_artist and get_user failed for %s: %s", channelId, user_error
                )
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "API structure error",
                        "message": "YouTube Music API has inconsistent header renderer formats",
                        "channelId": channelId,
                        "recommendation": "Try using /browse/user/{channelId} endpoint instead",
                        "technical_details": (
                            f"get_artist error: {error_str}, " f"get_user error: {user_error}"
                        ),
                    },
                ) from artist_error

        # Check for different page structure (might be a playlist/album page)
        if "singleColumnBrowseResultsRenderer" in error_str and (
            "musicResponsiveHeaderRenderer" in error_str or "musicDetailHeaderRenderer" in error_str
        ):
            logger.info(
                "Client attempted to use playlist/album ID '%s' on artist endpoint "
                "(detected by page structure)",
                channelId,
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Wrong endpoint",
                    "message": "This ID returns a playlist/album page, not an artist page",
                    "channelId": channelId,
                    "recommendation": (
                        "Use /playlists/{browseId} for playlists or "
                        "/browse/album/{browseId} for albums"
                    ),
                },
            ) from artist_error

        # If any other KeyError, re-raise to let the decorator handle
        raise artist_error

    if not search_results:
        raise HTTPException(status_code=404, detail="Artist not found")

    return {"message": "OK", "query": channelId, "result": search_results}


@router.get("/artist_videos/{channelId}")
@handle_browse_errors
async def get_artist_videos(channelId: str, ytmusic: YTMusic = Depends(get_ytmusic)):
    artist_results = ytmusic.get_artist(channelId)

    if not artist_results:
        raise HTTPException(status_code=404, detail="Artist not found")

    if "videos" not in artist_results or not artist_results["videos"]:
        raise HTTPException(status_code=404, detail="No videos found for this artist")

    browseId = artist_results["videos"]["browseId"]
    videos = ytmusic.get_playlist(browseId)

    return {"message": "OK", "query": channelId, "result": videos}


@router.get("/artist_albums/{channelId}")
@handle_browse_errors
async def get_artist_albums(
    channelId: str,
    params: str,
    limit: int | None = 100,
    order: Literal["Recency", "Popularity", "Alphabetical order"] | None = None,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    results = ytmusic.get_artist_albums(
        channelId=channelId, params=params, limit=limit, order=order
    )

    if not results:
        raise HTTPException(status_code=404, detail="No albums found for this artist")

    return {"message": "OK", "query": channelId, "result": results}


@router.get("/album/{browseId}")
@handle_browse_errors
async def get_album(browseId: str, ytmusic: YTMusic = Depends(get_ytmusic)):
    results = ytmusic.get_album(browseId)

    if not results:
        raise HTTPException(status_code=404, detail="Album not found")

    return {"message": "OK", "query": browseId, "result": results}


@router.get("/album_browse_id/{audioPlaylistId}")
@handle_browse_errors
async def get_album_browse_id(
    audioPlaylistId: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
    results = ytmusic.get_album_browse_id(audioPlaylistId)

    if not results:
        raise HTTPException(status_code=404, detail="Album browse ID not found")

    return {"message": "OK", "query": audioPlaylistId, "result": results}


@router.get("/user/{channelId}")
@handle_browse_errors
async def get_user(channelId: str, ytmusic: YTMusic = Depends(get_ytmusic)):
    # Perform ID validation first
    if channelId.startswith("VL") or channelId.startswith("OLAK") or channelId.startswith("PL"):
        logger.info("Client attempted to use playlist/album ID '%s' on user endpoint", channelId)
        if channelId.startswith("VL"):
            clean_id = channelId[2:]
            recommendation = f"Use /playlists/{clean_id} for playlists"
        elif channelId.startswith("OLAK"):
            recommendation = f"Use /playlists/{channelId} or /browse/album/{channelId} for albums"
        else:
            recommendation = f"Use /playlists/{channelId} for playlists"
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid ID type",
                "message": "This appears to be a playlist or album ID, not a user/channel ID",
                "channelId": channelId,
                "recommendation": recommendation,
            },
        )

    try:
        results = ytmusic.get_user(channelId)
    except Exception as user_error:
        error_str = str(user_error)
        if "musicVisualHeaderRenderer" in error_str and "musicImmersiveHeaderRenderer" in error_str:
            logger.info(
                "get_user failed for %s due to header renderer mismatch, "
                "trying get_artist fallback",
                channelId,
            )
            try:
                results = ytmusic.get_artist(channelId)
                logger.info("get_artist fallback successful for %s", channelId)
                return {
                    "message": "OK",
                    "query": channelId,
                    "result": results,
                    "note": "Retrieved using artist endpoint due to API structure changes",
                }
            except Exception as artist_error:
                logger.error(
                    "Both get_user and get_artist failed for %s: %s",
                    channelId,
                    artist_error,
                )
                raise HTTPException(
                    status_code=503,
                    detail={
                        "error": "API structure error",
                        "message": (
                            "YouTube Music API structure has changed (musicImmersiveHeaderRenderer "
                            "not yet supported by ytmusicapi)"
                        ),
                        "channelId": channelId,
                        "recommendation": "Try using /browse/artist/{channelId} endpoint instead",
                        "technical_details": error_str,
                    },
                ) from user_error
        # Otherwise raise to let decorator handle
        raise user_error

    if not results:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "OK", "query": channelId, "result": results}


@router.get("/user_playlists/{channelId}")
@handle_browse_errors
async def get_user_playlists(channelId: str, ytmusic: YTMusic = Depends(get_ytmusic)):
    channel = ytmusic.get_user(channelId)

    if not channel:
        raise HTTPException(status_code=404, detail="User not found")

    if "videos" not in channel or not channel["videos"] or "params" not in channel["videos"]:
        raise HTTPException(status_code=404, detail="User playlists not available")

    params = channel["videos"]["params"]
    results = ytmusic.get_user_playlists(channelId, params)

    return {"message": "OK", "query": channelId, "result": results}


@router.get("/user_videos/{channelId}")
@handle_browse_errors
async def get_user_videos(channelId: str, ytmusic: YTMusic = Depends(get_ytmusic)):
    channel = ytmusic.get_user(channelId)

    if not channel:
        raise HTTPException(status_code=404, detail="User not found")

    if "videos" not in channel or not channel["videos"] or "params" not in channel["videos"]:
        raise HTTPException(status_code=404, detail="User videos not available")

    params = channel["videos"]["params"]
    results = ytmusic.get_user_videos(channelId, params)

    return {"message": "OK", "query": channelId, "result": results}


@router.get("/song/{videoId}")
@handle_browse_errors
async def get_song(
    videoId: str,
    signatureTimestamp: int | None = None,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    results = ytmusic.get_song(videoId, signatureTimestamp)

    if not results:
        raise HTTPException(status_code=404, detail="Song not found")

    return {"message": "OK", "query": videoId, "result": results}


@router.get("/related/{browseId}")
@handle_browse_errors
async def get_related_by_browse_id(
    browseId: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
    results = ytmusic.get_song_related(browseId)

    if not results:
        raise HTTPException(status_code=404, detail="No related content found")

    return {"message": "OK", "query": browseId, "result": results}


@router.get("/song_related/{songId}")
@handle_browse_errors
async def get_song_related_by_song_id(
    songId: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
    # Try direct approach first (works for some song IDs)
    related_content = None
    related_browse_id = None

    try:
        related_content = ytmusic.get_song_related(songId)
        related_browse_id = songId
        logger.info("Direct get_song_related worked for %s", songId)
    except Exception as direct_error:
        logger.info(
            "Direct approach failed for %s, trying watch playlist: %s", songId, direct_error
        )

        # Fallback: Get watch playlist and extract related browse ID
        try:
            watch_playlist = ytmusic.get_watch_playlist(songId)

            if not watch_playlist or "related" not in watch_playlist:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "No related content available",
                        "message": "This song doesn't have related content available",
                        "songId": songId,
                    },
                ) from direct_error

            raw_related = watch_playlist.get("related")
            if not isinstance(raw_related, str):
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "No related content available",
                        "message": "This song doesn't have related content available",
                        "songId": songId,
                    },
                ) from direct_error

            related_browse_id = raw_related
            related_content = ytmusic.get_song_related(related_browse_id)
            logger.info(
                "Watch playlist approach worked for %s, browse ID: %s", songId, related_browse_id
            )

        except Exception as watch_error:
            logger.error(
                "Both approaches failed for %s: direct=%s, watch=%s",
                songId,
                direct_error,
                watch_error,
            )

            # Catch known bad request / invalid argument to raise a proper 400 bad request error
            error_msg = str(watch_error).lower()
            if "400" in error_msg and (
                "bad request" in error_msg or "invalid argument" in error_msg
            ):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid song ID",
                        "message": (
                            f"Song ID '{songId}' is not valid or cannot "
                            "be used to fetch related content"
                        ),
                        "songId": songId,
                        "recommendation": (
                            "Verify the song ID is correct and the song is publicly available"
                        ),
                    },
                ) from watch_error
            # Otherwise re-raise to let the decorator handle
            raise watch_error

    if not related_content:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "No related content available",
                "message": "No related songs found for this song ID",
                "songId": songId,
            },
        )

    # Also try to get basic song info for additional context
    song_info = None
    try:
        song_info = ytmusic.get_song(songId)
    except Exception:
        # If song info fails, continue with just related content
        pass

    return {
        "message": "OK",
        "songId": songId,
        "related_browse_id": related_browse_id,
        "related_content": related_content,
        "song_info": song_info,
        "total_related": len(related_content) if isinstance(related_content, list) else 0,
    }


@router.get("/lyrics/{browseId}")
@handle_browse_errors
async def get_lyrics(
    browseId: str,
    timestamps: bool | None = False,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    if timestamps:
        results = ytmusic.get_lyrics(browseId, True)
    else:
        results = ytmusic.get_lyrics(browseId)

    if not results:
        raise HTTPException(status_code=404, detail="Lyrics not found")

    return {"message": "OK", "query": browseId, "result": results}


@router.get("/tasteprofile")
@handle_browse_errors
async def get_tasteprofile(ytmusic: YTMusic = Depends(get_ytmusic)):
    results = ytmusic.get_tasteprofile()

    return {"message": "OK", "result": results}


@router.post("/tasteprofile")
@handle_browse_errors
async def set_tasteprofile(
    artists: list[str],
    taste_profile: dict | None = None,
    ytmusic: YTMusic = Depends(get_ytmusic),
):
    await execute_ytmusic_call(ytmusic.set_tasteprofile, artists, taste_profile)

    return {"message": "OK", "query": artists}


@router.get("/credits/{browseId}")
@handle_browse_errors
async def get_song_credits(
    browseId: str, ytmusic: YTMusic = Depends(get_ytmusic)
):
    """Retrieves song credits (performers, writers, producers) by browse ID."""
    results = await execute_ytmusic_call(ytmusic.get_song_credits, browseId)

    if not results:
        raise HTTPException(status_code=404, detail="Credits not found for this song")

    return {"message": "OK", "browseId": browseId, "result": results}


