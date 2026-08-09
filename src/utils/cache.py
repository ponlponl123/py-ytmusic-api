"""
Thread-safe TTL Caching and Threadpool utilities for YTMusic API responses.
Reduces network round-trips to YouTube Music and improves pod throughput.
Cache keys incorporate user session/auth identifiers for per-user isolation.
"""

import hashlib
from typing import Any, Callable
from cachetools import TTLCache
from starlette.concurrency import run_in_threadpool

# Memory cache for API responses (per-user + public queries)
# maxsize=1000 items, TTL=300 seconds (5 mins)
_ttl_cache: TTLCache = TTLCache(maxsize=1000, ttl=300)


def build_cache_key(prefix: str, auth_key: str | None = None, suffix: str | None = None) -> str:
    """
    Constructs a deterministic cache key scoped to a user session (or 'anonymous' if None).
    Hashes long auth/cookie strings using SHA-256 for clean, uniform cache key generation.
    """
    if auth_key:
        user_identifier = hashlib.sha256(auth_key.encode("utf-8")).hexdigest()[:16]
    else:
        user_identifier = "anonymous"

    if suffix:
        return f"{user_identifier}:{prefix}:{suffix}"
    return f"{user_identifier}:{prefix}"


async def execute_ytmusic_call(
    func: Callable, *args: Any, cache_key: str | None = None, **kwargs: Any
) -> Any:
    """
    Executes func(*args, **kwargs) asynchronously in Starlette's threadpool so
    synchronous requests calls in ytmusicapi never block the FastAPI event loop.

    If cache_key is provided and present in _ttl_cache, returns cached response immediately.
    """
    if cache_key and cache_key in _ttl_cache:
        return _ttl_cache[cache_key]

    result = await run_in_threadpool(func, *args, **kwargs)

    if cache_key and result is not None:
        _ttl_cache[cache_key] = result

    return result
