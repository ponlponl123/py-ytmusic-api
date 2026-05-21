"""
Integration test: search category enrichment.
Requires a live server at http://localhost:8000.
Run: pytest tests/integration/ -v -m integration
"""

import pytest
import requests

BASE_URL = "http://localhost:8000"
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module", autouse=True)
def require_server():
    """Skip all integration tests when the server is not reachable."""
    try:
        requests.get(f"{BASE_URL}/docs", timeout=2)
    except requests.exceptions.ConnectionError:
        pytest.skip("Live server not running at http://localhost:8000")


def test_search_all_results_have_categories():
    """All results from a broad search should have a non-null category after enrichment."""
    response = requests.get(
        f"{BASE_URL}/search/",
        params={"query": "nightcore", "limit": 10},
        timeout=30,
    )
    assert response.status_code == 200, f"Unexpected status: {response.status_code}"

    data = response.json()
    null_categories = [
        item for item in data["result"] if item.get("category") is None
    ]
    assert null_categories == [], (
        f"{len(null_categories)} results still have null category"
    )


def test_search_without_enrichment_returns_results():
    """Search with enrichment disabled should still return results."""
    response = requests.get(
        f"{BASE_URL}/search/",
        params={"query": "nightcore", "limit": 5, "enrich_categories": "false"},
        timeout=30,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["result"]) > 0
