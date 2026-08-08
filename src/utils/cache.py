"""
Thread-safe TTL Caching and Threadpool utilities for YTMusic API responses.
Reduces network round-trips to YouTube Music and improves pod throughput.
"""

from typing import Any, Callable
from cachetools import TTLCache
from starlette.concurrency import run_in_threadpool

# Memory cache for public (unauthenticated) queries
# maxsize=500 items, TTL=300 seconds (5 mins)
_public_ttl_cache: TTLCache = TTLCache(maxsize=500, ttl=300)


async def execute_ytmusic_call(
    func: Callable, *args: Any, cache_key: str | None = None, **kwargs: Any
) -> Any:
    """
    Executes func(*args, **kwargs) asynchronously in Starlette's threadpool so
    synchronous requests calls in ytmusicapi never block the FastAPI event loop.

    If cache_key is provided and present in _public_ttl_cache, returns cached response immediately.
    """
    if cache_key and cache_key in _public_ttl_cache:
        return _public_ttl_cache[cache_key]

    result = await run_in_threadpool(func, *args, **kwargs)

    if cache_key and result is not None:
        _public_ttl_cache[cache_key] = result

    return result
