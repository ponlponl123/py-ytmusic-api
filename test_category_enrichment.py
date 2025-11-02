"""Test script to verify category enrichment for search results"""
import requests
import json

def test_search_with_categories():
    """Test search endpoint with category enrichment"""
    base_url = "http://localhost:8000"
    
    # Test search with filter=None (all results)
    print("Testing search with filter 'all'...")
    response = requests.get(f"{base_url}/search/", params={
        "query": "nightcore",
        "limit": 10
    })
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nQuery: {data['query']}")
        print(f"Total results: {len(data['result'])}\n")
        
        # Check categories
        categories_found = {}
        null_categories = 0
        
        for idx, item in enumerate(data['result'], 1):
            category = item.get('category')
            result_type = item.get('resultType')
            title = item.get('title') or item.get('artist') or 'N/A'
            
            print(f"{idx}. [{result_type}] {title[:50]}")
            print(f"   Category: {category}")
            
            if category:
                categories_found[category] = categories_found.get(category, 0) + 1
            else:
                null_categories += 1
        
        print(f"\n--- Summary ---")
        print(f"Results with categories: {len(data['result']) - null_categories}")
        print(f"Results with null category: {null_categories}")
        print(f"\nCategory distribution:")
        for cat, count in categories_found.items():
            print(f"  {cat}: {count}")
        
        return null_categories == 0  # Success if no null categories
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False


def test_search_without_enrichment():
    """Test search with enrichment disabled"""
    base_url = "http://localhost:8000"
    
    print("\n\n=== Testing WITHOUT category enrichment ===")
    response = requests.get(f"{base_url}/search/", params={
        "query": "nightcore",
        "limit": 5,
        "enrich_categories": "false"
    })
    
    if response.status_code == 200:
        data = response.json()
        null_count = sum(1 for item in data['result'] if item.get('category') is None)
        print(f"Results with null category: {null_count}/{len(data['result'])}")
        return True
    else:
        print(f"Error: {response.status_code}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Category Enrichment Feature")
    print("=" * 60)
    
    # Make sure the server is running
    try:
        success1 = test_search_with_categories()
        success2 = test_search_without_enrichment()
        
        print("\n" + "=" * 60)
        if success1:
            print("✅ Category enrichment working correctly!")
        else:
            print("❌ Some categories are still null")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Please make sure the API is running on http://localhost:8000")
