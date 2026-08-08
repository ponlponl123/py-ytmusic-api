"""
High-Concurrency Benchmark & Load Testing Suite for py-ytmusic-api.

Measures concurrency throughput (RPS), latency percentiles (p50, p90, p99),
threadpool non-blocking event-loop performance, and TTL cache effectiveness.
"""

import asyncio
from pathlib import Path
import sys
import time
from typing import Any
from unittest.mock import MagicMock

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from httpx import ASGITransport, AsyncClient
from src.main import app
from src.utils.client import YTMusicClient


def setup_mock_ytmusic():
    """Mocks backend YTMusic call with simulated 50ms I/O network delay."""
    mock_ytmusic = MagicMock()

    def mock_get_explore(*args, **kwargs):
        time.sleep(0.05)  # Simulate 50ms YouTube Music API network latency
        return {"categories": ["Trending", "Moods"], "items": [i for i in range(20)]}

    def mock_search(query, *args, **kwargs):
        time.sleep(0.05)
        return [{"title": f"Result {i} for {query}"} for i in range(10)]

    mock_ytmusic.get_explore.side_effect = mock_get_explore
    mock_ytmusic.search.side_effect = mock_search
    return mock_ytmusic


async def run_concurrent_requests(
    client: AsyncClient, url: str, num_requests: int, headers: dict[str, str] | None = None
) -> tuple[float, list[float], int]:
    """Fires num_requests concurrently and measures total time and individual latencies."""
    latencies: list[float] = []
    successful: int = 0

    async def single_request():
        nonlocal successful
        start = time.perf_counter()
        res = await client.get(url, headers=headers)
        duration = time.perf_counter() - start
        if res.status_code == 200:
            successful += 1
            latencies.append(duration * 1000)  # ms

    start_total = time.perf_counter()
    tasks = [asyncio.create_task(single_request()) for _ in range(num_requests)]
    await asyncio.gather(*tasks)
    total_time = time.perf_counter() - start_total

    return total_time, latencies, successful


def calculate_percentiles(latencies: list[float]) -> dict[str, float]:
    if not latencies:
        return {"p50": 0.0, "p90": 0.0, "p99": 0.0, "avg": 0.0}
    sorted_l = sorted(latencies)
    n = len(sorted_l)
    return {
        "avg": sum(sorted_l) / n,
        "p50": sorted_l[int(n * 0.50)],
        "p90": sorted_l[int(n * 0.90)],
        "p99": sorted_l[int(min(n - 1, int(n * 0.99)))],
    }


async def main():
    import logging
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("src.main").setLevel(logging.WARNING)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("py-ytmusic-api High-Concurrency Performance & Load Benchmark")
    print("=" * 80)

    mock_ytmusic = setup_mock_ytmusic()
    YTMusicClient.get_client = MagicMock(return_value=mock_ytmusic)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        # Warmup
        await client.get("/explore/explore")

        # Scenario 1: Threadpool Offloading under 200 Concurrent Uncached Requests
        print("\n--- Benchmark 1: Threadpool Offloading (200 Concurrent Requests, 50ms Simulated I/O) ---")
        num_reqs = 200
        total_sec, latencies, ok_count = await run_concurrent_requests(
            client, "/search/?query=test_bench", num_reqs
        )
        stats = calculate_percentiles(latencies)
        rps = ok_count / total_sec

        print(f"   - Total Requests: {num_reqs}")
        print(f"   - Successful Responses: {ok_count}/{num_reqs}")
        print(f"   - Total Execution Time: {total_sec:.2f}s")
        print(f"   - Throughput (RPS): {rps:.2f} req/sec")
        print(f"   - Latency Avg: {stats['avg']:.2f} ms")
        print(f"   - Latency p50: {stats['p50']:.2f} ms | p90: {stats['p90']:.2f} ms | p99: {stats['p99']:.2f} ms")

        # Scenario 2: TTL Cache Efficiency under 1,000 Concurrent Requests
        print("\n--- Benchmark 2: Memory TTL Cache (1,000 Concurrent Requests on /explore/explore) ---")
        num_reqs_cache = 1000
        total_sec_cache, latencies_cache, ok_count_cache = await run_concurrent_requests(
            client, "/explore/explore", num_reqs_cache
        )
        stats_cache = calculate_percentiles(latencies_cache)
        rps_cache = ok_count_cache / total_sec_cache

        print(f"   - Total Requests: {num_reqs_cache}")
        print(f"   - Successful Responses: {ok_count_cache}/{num_reqs_cache}")
        print(f"   - Total Execution Time: {total_sec_cache:.3f}s")
        print(f"   - Throughput (RPS): {rps_cache:.2f} req/sec")
        print(f"   - Latency Avg: {stats_cache['avg']:.2f} ms")
        print(f"   - Latency p50: {stats_cache['p50']:.2f} ms | p90: {stats_cache['p90']:.2f} ms | p99: {stats_cache['p99']:.2f} ms")

        # Scenario 3: Per-User Cookie Auth Isolation under Concurrent Traffic
        print("\n--- Benchmark 3: Per-User Cookie Session Isolation (50 Distinct Users Concurrent) ---")
        tasks = []
        user_latencies = []
        start_user = time.perf_counter()

        async def user_request(user_id: int):
            headers = {"x-ytmusic-cookie": f"user_cookie_session_{user_id}"}
            t0 = time.perf_counter()
            res = await client.get("/explore/explore", headers=headers)
            user_latencies.append((time.perf_counter() - t0) * 1000)
            assert res.status_code == 200

        await asyncio.gather(*[user_request(i) for i in range(50)])
        total_user_time = time.perf_counter() - start_user
        stats_user = calculate_percentiles(user_latencies)

        print(f"   - Total User Sessions Created: 50")
        print(f"   - Total Execution Time: {total_user_time:.2f}s")
        print(f"   - Latency Avg: {stats_user['avg']:.2f} ms")
        print(f"   - Cache Session Count in LRU: {len(YTMusicClient._cookie_clients)}")

    print("\n" + "=" * 80)
    print("Benchmark Completed Successfully")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
