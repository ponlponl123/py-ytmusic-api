"""
Comprehensive error handling utilities for YTMusic API wrapper
"""

import logging
from functools import wraps
from typing import Any, Callable

from fastapi import HTTPException

logger = logging.getLogger(__name__)


class YTMusicErrorHandler:
    """Centralized error handling for YTMusic API operations"""

    @staticmethod
    def handle_common_errors(operation_name: str, identifier: str = None):
        """
        Decorator to handle common YTMusic API errors

        Args:
            operation_name: Name of the operation for logging and error messages
            identifier: Optional identifier (like videoId, channelId) for context
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)

                except KeyError as e:
                    import traceback
                    error_traceback = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                    logger.error(
                        f"KeyError in {operation_name}{f' for {identifier}' if identifier else ''}: {str(e)}\n"
                        f"Traceback:\n{error_traceback}"
                    )

                    # Provide more specific error messages based on the KeyError
                    if "header" in str(e):
                        detail = {
                            "error": "API structure changed",
                            "message": "YouTube Music changed their response structure. This is a known issue that occurs when YouTube updates their API.",
                            "operation": operation_name,
                            "solution": "Try again later or use simpler search parameters",
                            "technical_details": str(e),
                        }
                    else:
                        detail = {
                            "error": "API parsing error",
                            "message": f"YouTube Music API structure has changed, {operation_name.replace('_', ' ')} temporarily unavailable",
                            "operation": operation_name,
                            "technical_details": str(e),
                        }

                    if identifier:
                        detail["identifier"] = identifier

                    raise HTTPException(status_code=503, detail=detail)

                except ValueError as e:
                    logger.error(
                        f"ValueError in {operation_name}{f' for {identifier}' if identifier else ''}: {str(e)}"
                    )
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Invalid input",
                            "message": f"Invalid parameter provided: {str(e)}",
                            "operation": operation_name,
                            "identifier": identifier,
                        },
                    )

                except ConnectionError as e:
                    logger.error(f"ConnectionError in {operation_name}: {str(e)}")
                    raise HTTPException(
                        status_code=503,
                        detail={
                            "error": "Connection failed",
                            "message": "Unable to connect to YouTube Music. Please check your internet connection.",
                            "operation": operation_name,
                        },
                    )

                except TimeoutError as e:
                    logger.error(f"TimeoutError in {operation_name}: {str(e)}")
                    raise HTTPException(
                        status_code=504,
                        detail={
                            "error": "Request timeout",
                            "message": "Request to YouTube Music timed out. Please try again.",
                            "operation": operation_name,
                        },
                    )

                except Exception as e:
                    import traceback
                    error_traceback = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                    logger.error(
                        f"Unexpected error in {operation_name}{f' for {identifier}' if identifier else ''}: "
                        f"{type(e).__name__}: {str(e)}\n"
                        f"Traceback:\n{error_traceback}"
                    )

                    error_message = str(e).lower()

                    # Authentication errors
                    if any(
                        keyword in error_message
                        for keyword in ["auth", "login", "unauthorized", "credentials"]
                    ):
                        raise HTTPException(
                            status_code=401,
                            detail={
                                "error": "Authentication required",
                                "message": f"Authentication required to access {operation_name.replace('_', ' ')}",
                                "operation": operation_name,
                            },
                        )

                    # Not found errors
                    elif any(
                        keyword in error_message
                        for keyword in ["not found", "unavailable", "does not exist"]
                    ):
                        status_code = 404
                        if identifier:
                            message = f"Content with ID {identifier} not found or unavailable"
                        else:
                            message = f"{operation_name.replace('_', ' ').title()} not found"

                        raise HTTPException(
                            status_code=status_code,
                            detail={
                                "error": "Not found",
                                "message": message,
                                "operation": operation_name,
                                "identifier": identifier,
                            },
                        )

                    # Permission/access errors
                    elif any(
                        keyword in error_message
                        for keyword in ["permission", "forbidden", "access denied"]
                    ):
                        raise HTTPException(
                            status_code=403,
                            detail={
                                "error": "Access forbidden",
                                "message": f"You don't have permission to access {operation_name.replace('_', ' ')}",
                                "operation": operation_name,
                            },
                        )

                    # Rate limiting errors
                    elif any(
                        keyword in error_message
                        for keyword in ["quota", "limit", "rate", "too many requests"]
                    ):
                        raise HTTPException(
                            status_code=429,
                            detail={
                                "error": "Rate limit exceeded",
                                "message": "API rate limit exceeded. Please try again later.",
                                "operation": operation_name,
                                "retry_after": "60",  # Suggest waiting 60 seconds
                            },
                        )

                    # Invalid format/parameter errors
                    elif any(
                        keyword in error_message
                        for keyword in ["invalid", "format", "unsupported", "malformed"]
                    ):
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "error": "Invalid input",
                                "message": f"Invalid input provided: {str(e)}",
                                "operation": operation_name,
                                "identifier": identifier,
                            },
                        )

                    # Generic server error
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail={
                                "error": "Internal server error",
                                "message": f"An unexpected error occurred while {operation_name.replace('_', ' ')}",
                                "operation": operation_name,
                                "identifier": identifier,
                            },
                        )

            return wrapper

        return decorator

    @staticmethod
    def validate_video_id(video_id: str) -> None:
        """Validate YouTube video ID format"""
        if not video_id or len(video_id) != 11:
            raise ValueError(f"Invalid video ID format: {video_id}")

    @staticmethod
    def validate_channel_id(channel_id: str) -> None:
        """Validate YouTube channel ID format"""
        if not channel_id or not (channel_id.startswith("UC") and len(channel_id) == 24):
            raise ValueError(f"Invalid channel ID format: {channel_id}")

    @staticmethod
    def validate_playlist_id(playlist_id: str) -> None:
        """Validate YouTube playlist ID format"""
        valid_prefixes = ["PL", "UU", "LL", "RD", "WL", "OL"]
        if not playlist_id or not any(playlist_id.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(f"Invalid playlist ID format: {playlist_id}")


# Convenience decorators for common operations
def handle_search_errors(func):
    """Decorator specifically for search operations"""
    return YTMusicErrorHandler.handle_common_errors("search")(func)


def handle_browse_errors(func):
    """Decorator specifically for browse operations"""
    return YTMusicErrorHandler.handle_common_errors("browse")(func)


def handle_library_errors(func):
    """Decorator specifically for library operations"""
    return YTMusicErrorHandler.handle_common_errors("library_access")(func)


def handle_playlist_errors(func):
    """Decorator specifically for playlist operations"""
    return YTMusicErrorHandler.handle_common_errors("playlist_operation")(func)


def handle_upload_errors(func):
    """Decorator specifically for upload operations"""
    return YTMusicErrorHandler.handle_common_errors("upload_operation")(func)
