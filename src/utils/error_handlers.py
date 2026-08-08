"""
Comprehensive error handling utilities for YTMusic API wrapper
"""

import asyncio
import logging
import traceback
from functools import wraps
from typing import Callable, Optional

from fastapi import HTTPException
from ytmusicapi.exceptions import YTMusicUserError

logger = logging.getLogger(__name__)


class YTMusicErrorHandler:
    """Centralized error handling for YTMusic API operations"""

    @staticmethod
    def _handle_key_error(e: KeyError, operation_name: str, identifier: Optional[str] = None):
        error_traceback = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        ident_str = f" for {identifier}" if identifier else ""
        logger.error(
            "KeyError in %s%s: %s\nTraceback:\n%s",
            operation_name,
            ident_str,
            str(e),
            error_traceback,
        )

        # Provide more specific error messages based on the KeyError
        if "header" in str(e):
            detail = {
                "error": "API structure changed",
                "message": (
                    "YouTube Music changed their response structure. "
                    "This is a known issue that occurs when YouTube updates their API."
                ),
                "operation": operation_name,
                "solution": "Try again later or use simpler search parameters",
                "technical_details": str(e),
            }
        else:
            detail = {
                "error": "API parsing error",
                "message": (
                    f"YouTube Music API structure has changed, "
                    f"{operation_name.replace('_', ' ')} temporarily unavailable"
                ),
                "operation": operation_name,
                "technical_details": str(e),
            }

        if identifier:
            detail["identifier"] = identifier

        raise HTTPException(status_code=503, detail=detail)

    @staticmethod
    def _handle_user_error(e: Exception, operation_name: str, identifier: Optional[str] = None):
        ident_str = f" for {identifier}" if identifier else ""
        logger.info("User/Client error in %s%s: %s", operation_name, ident_str, str(e))
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid request",
                "message": str(e),
                "operation": operation_name,
                "identifier": identifier,
            },
        )

    @staticmethod
    def _handle_value_error(e: ValueError, operation_name: str, identifier: Optional[str] = None):
        ident_str = f" for {identifier}" if identifier else ""
        logger.error("ValueError in %s%s: %s", operation_name, ident_str, str(e))
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid input",
                "message": f"Invalid parameter provided: {str(e)}",
                "operation": operation_name,
                "identifier": identifier,
            },
        )

    @staticmethod
    def _handle_connection_error(e: ConnectionError, operation_name: str):
        logger.error("ConnectionError in %s: %s", operation_name, str(e))
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Connection failed",
                "message": (
                    "Unable to connect to YouTube Music. " "Please check your internet connection."
                ),
                "operation": operation_name,
            },
        )

    @staticmethod
    def _handle_timeout_error(e: TimeoutError, operation_name: str):
        logger.error("TimeoutError in %s: %s", operation_name, str(e))
        raise HTTPException(
            status_code=504,
            detail={
                "error": "Request timeout",
                "message": "Request to YouTube Music timed out. Please try again.",
                "operation": operation_name,
            },
        )

    @staticmethod
    def _handle_generic_exception(
        e: Exception, operation_name: str, identifier: Optional[str] = None
    ):
        error_traceback = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        ident_str = f" for {identifier}" if identifier else ""
        logger.error(
            "Unexpected error in %s%s: %s: %s\nTraceback:\n%s",
            operation_name,
            ident_str,
            type(e).__name__,
            str(e),
            error_traceback,
        )

        error_message = str(e).lower()

        # Authentication errors
        if any(
            keyword in error_message for keyword in ["auth", "login", "unauthorized", "credentials"]
        ):
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Authentication required",
                    "message": (
                        f"Authentication required to access {operation_name.replace('_', ' ')}"
                    ),
                    "operation": operation_name,
                },
            )

        # Not found errors
        if any(
            keyword in error_message for keyword in ["not found", "unavailable", "does not exist"]
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
        if any(
            keyword in error_message for keyword in ["permission", "forbidden", "access denied"]
        ):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Access forbidden",
                    "message": (
                        f"You don't have permission to access {operation_name.replace('_', ' ')}"
                    ),
                    "operation": operation_name,
                },
            )

        # Rate limiting errors
        if any(
            keyword in error_message for keyword in ["quota", "limit", "rate", "too many requests"]
        ):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "message": "API rate limit exceeded. Please try again later.",
                    "operation": operation_name,
                    "retry_after": "60",
                },
            )

        # Invalid format/parameter errors
        if any(
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
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": f"An unexpected error occurred while {operation_name.replace('_', ' ')}",
                "operation": operation_name,
                "identifier": identifier,
            },
        )

    @staticmethod
    def handle_common_errors(operation_name: str, identifier: Optional[str] = None):
        """
        Decorator to handle common YTMusic API errors. Supports both sync and async routes.

        Args:
            operation_name: Name of the operation for logging and error messages
            identifier: Optional identifier (like videoId, channelId) for context
        """

        def decorator(func: Callable) -> Callable:
            if asyncio.iscoroutinefunction(func):

                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    try:
                        return await func(*args, **kwargs)
                    except HTTPException:
                        raise
                    except YTMusicUserError as e:
                        YTMusicErrorHandler._handle_user_error(e, operation_name, identifier)
                    except KeyError as e:
                        YTMusicErrorHandler._handle_key_error(e, operation_name, identifier)
                    except ValueError as e:
                        YTMusicErrorHandler._handle_value_error(e, operation_name, identifier)
                    except ConnectionError as e:
                        YTMusicErrorHandler._handle_connection_error(e, operation_name)
                    except TimeoutError as e:
                        YTMusicErrorHandler._handle_timeout_error(e, operation_name)
                    except Exception as e:
                        YTMusicErrorHandler._handle_generic_exception(e, operation_name, identifier)

                return async_wrapper

            # pylint: disable=inconsistent-return-statements
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except HTTPException:
                    raise
                except YTMusicUserError as e:
                    YTMusicErrorHandler._handle_user_error(e, operation_name, identifier)
                except KeyError as e:
                    YTMusicErrorHandler._handle_key_error(e, operation_name, identifier)
                except ValueError as e:
                    YTMusicErrorHandler._handle_value_error(e, operation_name, identifier)
                except ConnectionError as e:
                    YTMusicErrorHandler._handle_connection_error(e, operation_name)
                except TimeoutError as e:
                    YTMusicErrorHandler._handle_timeout_error(e, operation_name)
                except Exception as e:
                    YTMusicErrorHandler._handle_generic_exception(e, operation_name, identifier)

            return sync_wrapper

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
