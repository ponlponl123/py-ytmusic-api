#!/usr/bin/env python3
"""
Test the fixed song related endpoint directly
"""
import sys
sys.path.insert(0, "src")

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

# Test both song IDs
test_songs = [
    "MPTRt_J06gtxzw8Sv",  # Originally working one
    "b3rFbkFjRrA"         # Previously problematic one
]

for song_id in test_songs:
    print(f"\n{'='*50}")
    print(f"Testing song ID: {song_id}")
    print(f"{'='*50}")
    
    response = client.get(f"/browse/song_related/{song_id}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS!")
        print(f"Related browse ID: {result.get('related_browse_id', 'N/A')}")
        print(f"Total related sections: {result.get('total_related', 0)}")
        if result.get('related_content'):
            print(f"First section title: {result['related_content'][0].get('title', 'N/A')}")
    else:
        print(f"❌ FAILED: {response.json()}")