import logging
from typing import Literal

from fastapi import APIRouter, HTTPException
from ytmusicapi import YTMusic

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/home")
async def get_home(limit: int = 3):
    try:
        ytmusic = YTMusic()
        search_results = ytmusic.get_home(limit)

        if not search_results:
            raise HTTPException(status_code=404, detail="No home content found")

        return {"message": "OK", "limit": limit, "result": search_results}

    except KeyError as e:
        logger.error(f"KeyError in get_home: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, home content temporarily unavailable",
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_home: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching home content",
            },
        )


@router.get("/artist/{channelId}")
async def get_artist(channelId: str):
    try:
        ytmusic = YTMusic()
        search_results = ytmusic.get_artist(channelId)

        if not search_results:
            raise HTTPException(status_code=404, detail="Artist not found")

        return {"message": "OK", "query": channelId, "result": search_results}

    except KeyError as e:
        logger.error(f"KeyError in get_artist for {channelId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, artist data temporarily unavailable",
                "channelId": channelId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_artist for {channelId}: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Artist with ID {channelId} not found")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching artist data",
                "channelId": channelId,
            },
        )


@router.get("/artist_videos/{channelId}")
async def get_artist_videos(channelId: str):
    try:
        ytmusic = YTMusic()
        artist_results = ytmusic.get_artist(channelId)

        if not artist_results:
            raise HTTPException(status_code=404, detail="Artist not found")

        # Check if videos section exists
        if "videos" not in artist_results or not artist_results["videos"]:
            raise HTTPException(status_code=404, detail="No videos found for this artist")

        browseId = artist_results["videos"]["browseId"]
        videos = ytmusic.get_playlist(browseId)

        return {"message": "OK", "query": channelId, "result": videos}

    except HTTPException:
        raise  # Re-raise HTTP exceptions as they are

    except KeyError as e:
        logger.error(f"KeyError in get_artist_videos for {channelId}: {str(e)}")

        # Try to provide more specific error based on which key is missing
        if "videos" in str(e):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "No videos available",
                    "message": "This artist doesn't have videos available or the structure has changed",
                    "channelId": channelId,
                },
            )

        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, artist videos temporarily unavailable",
                "channelId": channelId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_artist_videos for {channelId}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching artist videos",
                "channelId": channelId,
            },
        )


@router.get("/artist_albums/{channelId}")
async def get_artist_albums(
    channelId: str,
    params: str,
    limit: int | None = 100,
    order: Literal["Recency", "Popularity", "Alphabetical order"] | None = None,
):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_artist_albums(
            channelId=channelId, params=params, limit=limit, order=order
        )

        if not results:
            raise HTTPException(status_code=404, detail="No albums found for this artist")

        return {"message": "OK", "query": channelId, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_artist_albums for {channelId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, artist albums temporarily unavailable",
                "channelId": channelId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_artist_albums for {channelId}: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Artist with ID {channelId} not found")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching artist albums",
                "channelId": channelId,
            },
        )


@router.get("/album/{browseId}")
async def get_album(browseId: str):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_album(browseId)

        if not results:
            raise HTTPException(status_code=404, detail="Album not found")

        return {"message": "OK", "query": browseId, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_album for {browseId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, album data temporarily unavailable",
                "browseId": browseId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_album for {browseId}: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Album with ID {browseId} not found")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching album data",
                "browseId": browseId,
            },
        )


@router.get("/album_browse_id/{audioPlaylistId}")
async def get_album_browse_id(audioPlaylistId: str):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_album_browse_id(audioPlaylistId)

        if not results:
            raise HTTPException(status_code=404, detail="Album browse ID not found")

        return {"message": "OK", "query": audioPlaylistId, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_album_browse_id for {audioPlaylistId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, album browse ID temporarily unavailable",
                "audioPlaylistId": audioPlaylistId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_album_browse_id for {audioPlaylistId}: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=404, detail=f"Album with playlist ID {audioPlaylistId} not found"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching album browse ID",
                "audioPlaylistId": audioPlaylistId,
            },
        )


@router.get("/user/{channelId}")
async def get_user(channelId: str):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_user(channelId)

        if not results:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "OK", "query": channelId, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_user for {channelId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, user data temporarily unavailable",
                "channelId": channelId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_user for {channelId}: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"User with ID {channelId} not found")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching user data",
                "channelId": channelId,
            },
        )


@router.get("/user_playlists/{channelId}")
async def get_user_playlists(channelId: str):
    try:
        ytmusic = YTMusic()
        channel = ytmusic.get_user(channelId)

        if not channel:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if videos section exists and has params
        if "videos" not in channel or not channel["videos"] or "params" not in channel["videos"]:
            raise HTTPException(status_code=404, detail="User playlists not available")

        params = channel["videos"]["params"]
        results = ytmusic.get_user_playlists(channelId, params)

        return {"message": "OK", "query": channelId, "result": results}

    except HTTPException:
        raise  # Re-raise HTTP exceptions as they are

    except KeyError as e:
        logger.error(f"KeyError in get_user_playlists for {channelId}: {str(e)}")

        if "videos" in str(e) or "params" in str(e):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Playlists not available",
                    "message": "This user doesn't have accessible playlists or the structure has changed",
                    "channelId": channelId,
                },
            )

        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, user playlists temporarily unavailable",
                "channelId": channelId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_user_playlists for {channelId}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching user playlists",
                "channelId": channelId,
            },
        )


@router.get("/user_videos/{channelId}")
async def get_user_videos(channelId: str):
    try:
        ytmusic = YTMusic()
        channel = ytmusic.get_user(channelId)

        if not channel:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if videos section exists and has params
        if "videos" not in channel or not channel["videos"] or "params" not in channel["videos"]:
            raise HTTPException(status_code=404, detail="User videos not available")

        params = channel["videos"]["params"]
        results = ytmusic.get_user_videos(channelId, params)

        return {"message": "OK", "query": channelId, "result": results}

    except HTTPException:
        raise  # Re-raise HTTP exceptions as they are

    except KeyError as e:
        logger.error(f"KeyError in get_user_videos for {channelId}: {str(e)}")

        if "videos" in str(e) or "params" in str(e):
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Videos not available",
                    "message": "This user doesn't have accessible videos or the structure has changed",
                    "channelId": channelId,
                },
            )

        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, user videos temporarily unavailable",
                "channelId": channelId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_user_videos for {channelId}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching user videos",
                "channelId": channelId,
            },
        )


@router.get("/song/{videoId}")
async def get_song(videoId: str, signatureTimestamp: int | None = None):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_song(videoId, signatureTimestamp)

        if not results:
            raise HTTPException(status_code=404, detail="Song not found")

        return {"message": "OK", "query": videoId, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_song for {videoId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, song data temporarily unavailable",
                "videoId": videoId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_song for {videoId}: {str(e)}")
        if "not found" in str(e).lower() or "unavailable" in str(e).lower():
            raise HTTPException(
                status_code=404, detail=f"Song with ID {videoId} not found or unavailable"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching song data",
                "videoId": videoId,
            },
        )


@router.get("/related/{browseId}")
async def get_related_by_browse_id(browseId: str):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_song_related(browseId)

        if not results:
            raise HTTPException(status_code=404, detail="No related content found")

        return {"message": "OK", "query": browseId, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_related_by_browse_id for {browseId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, related content temporarily unavailable",
                "browseId": browseId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_related_by_browse_id for {browseId}: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Related content for {browseId} not found")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching related content",
                "browseId": browseId,
            },
        )


@router.get("/song_related/{songId}")
async def get_song_related_by_song_id(songId: str):
    try:
        ytmusic = YTMusic()
        
        # Try direct approach first (works for some song IDs)
        related_content = None
        related_browse_id = None
        
        try:
            related_content = ytmusic.get_song_related(songId)
            related_browse_id = songId
            logger.info("Direct get_song_related worked for %s", songId)
        except Exception as direct_error:
            logger.info("Direct approach failed for %s, trying watch playlist: %s", songId, str(direct_error))
            
            # Fallback: Get watch playlist and extract related browse ID
            try:
                watch_playlist = ytmusic.get_watch_playlist(songId)
                
                if not watch_playlist or 'related' not in watch_playlist:
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "error": "No related content available", 
                            "message": "This song doesn't have related content available",
                            "songId": songId
                        }
                    )
                
                related_browse_id = watch_playlist['related']
                related_content = ytmusic.get_song_related(related_browse_id)
                logger.info("Watch playlist approach worked for %s, browse ID: %s", songId, related_browse_id)
                
            except Exception as watch_error:
                logger.error("Both approaches failed for %s: direct=%s, watch=%s", songId, str(direct_error), str(watch_error))
                raise watch_error

        if not related_content:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "No related content available",
                    "message": "No related songs found for this song ID",
                    "songId": songId
                }
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
            "total_related": len(related_content) if isinstance(related_content, list) else 0
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions as they are

    except KeyError as e:
        logger.error("KeyError in get_song_related_by_song_id for %s: %s", songId, str(e))

        if "header" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "API structure error",
                    "message": "YouTube Music API structure has changed, song related content temporarily unavailable",
                    "songId": songId,
                    "technical_details": str(e),
                },
            ) from e

        raise HTTPException(
            status_code=404,
            detail={
                "error": "Related content not available",
                "message": "Related content structure has changed or is not available for this song",
                "songId": songId,
            },
        ) from e

    except Exception as e:
        logger.error("Unexpected error in get_song_related_by_song_id for %s: %s", songId, str(e))
        
        error_msg = str(e).lower()
        
        if "400" in error_msg and ("bad request" in error_msg or "invalid argument" in error_msg):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid song ID",
                    "message": f"Song ID '{songId}' is not valid or cannot be used to fetch related content",
                    "songId": songId,
                    "recommendation": "Verify the song ID is correct and the song is publicly available"
                }
            ) from e
        
        if "not found" in error_msg or "unavailable" in error_msg:
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": "Song not found",
                    "message": f"Song with ID {songId} not found or unavailable",
                    "songId": songId
                }
            ) from e
        
        if "private" in error_msg or "access" in error_msg or "401" in error_msg:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Access denied",
                    "message": "This song may be private or region-restricted",
                    "songId": songId
                }
            ) from e

        # Check for server errors from YouTube Music
        if "server returned http" in error_msg:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "YouTube Music API error",
                    "message": "YouTube Music service is experiencing issues",
                    "songId": songId,
                    "technical_details": str(e)
                }
            ) from e

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching song related content",
                "songId": songId,
                "technical_details": str(e)
            },
        ) from e


@router.get("/lyrics/{browseId}")
async def get_lyrics(browseId: str, timestamps: bool | None = False):
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_lyrics(browseId, timestamps)

        if not results:
            raise HTTPException(status_code=404, detail="Lyrics not found")

        return {"message": "OK", "query": browseId, "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_lyrics for {browseId}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, lyrics temporarily unavailable",
                "browseId": browseId,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_lyrics for {browseId}: {str(e)}")
        if "not found" in str(e).lower() or "no lyrics" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Lyrics for {browseId} not found")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching lyrics",
                "browseId": browseId,
            },
        )


@router.get("/tasteprofile")
async def get_tasteprofile():
    try:
        ytmusic = YTMusic()
        results = ytmusic.get_tasteprofile()

        return {"message": "OK", "result": results}

    except KeyError as e:
        logger.error(f"KeyError in get_tasteprofile: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, taste profile temporarily unavailable",
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_tasteprofile: {str(e)}")
        if "auth" in str(e).lower() or "login" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to access taste profile"
            )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while fetching taste profile",
            },
        )


@router.post("/tasteprofile")
async def set_tasteprofile(artists: list[str], taste_profile: dict | None = None):
    try:
        ytmusic = YTMusic()
        ytmusic.set_tasteprofile(artists, taste_profile)

        return {"message": "OK", "query": artists}

    except KeyError as e:
        logger.error(f"KeyError in set_tasteprofile: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "API structure error",
                "message": "YouTube Music API structure has changed, cannot set taste profile",
                "artists": artists,
                "technical_details": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Unexpected error in set_tasteprofile: {str(e)}")
        if "auth" in str(e).lower() or "login" in str(e).lower():
            raise HTTPException(
                status_code=401, detail="Authentication required to set taste profile"
            )
        elif "invalid" in str(e).lower():
            raise HTTPException(status_code=400, detail=f"Invalid input data: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while setting taste profile",
                "artists": artists,
            },
        )
