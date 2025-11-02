"""Test wrong endpoint usage - playlist ID on artist endpoint"""

import requests

BASE_URL = "http://localhost:8000"

def test_playlist_id_on_artist_endpoint():
    """Test that playlist IDs are properly detected and rejected on artist endpoint"""
    
    # This is a playlist/album ID, not an artist ID
    playlist_id = "VLOLAK5uy_m-Cz9P8WPZNzB_FdLxx5Gw3tYc5MetaLI"
    
    print(f"\n🧪 Testing /browse/artist/{playlist_id}")
    print("=" * 70)
    print("This should return a helpful error since it's a playlist ID")
    print("-" * 70)
    
    response = requests.get(f"{BASE_URL}/browse/artist/{playlist_id}", timeout=30)
    
    print(f"\nStatus Code: {response.status_code}", end=" ")
    if response.status_code == 400:
        print("✅ CORRECT (400 Bad Request)")
    elif response.status_code == 503:
        print("⚠️  SERVICE UNAVAILABLE (needs better detection)")
    else:
        print(f"❌ UNEXPECTED")
    
    data = response.json()
    print(f"\nResponse:")
    if 'detail' in data:
        detail = data['detail']
        if isinstance(detail, dict):
            print(f"  Error: {detail.get('error')}")
            print(f"  Message: {detail.get('message')}")
            if 'recommendation' in detail:
                print(f"  Recommendation: {detail.get('recommendation')}")
        else:
            print(f"  {detail}")
    
    print("=" * 70)


def test_correct_endpoints():
    """Test the correct endpoints for comparison"""
    
    # Test playlist endpoint
    playlist_id = "OLAK5uy_m-Cz9P8WPZNzB_FdLxx5Gw3tYc5MetaLI"
    
    print(f"\n🧪 Testing correct endpoint: /playlists/{playlist_id}")
    print("=" * 70)
    
    response = requests.get(f"{BASE_URL}/playlists/{playlist_id}", timeout=30)
    
    print(f"Status Code: {response.status_code}", end=" ")
    if response.status_code == 200:
        print("✅ SUCCESS!")
        data = response.json()
        if 'result' in data:
            result = data['result']
            if 'title' in result:
                print(f"  Title: {result['title']}")
            if 'trackCount' in result:
                print(f"  Tracks: {result['trackCount']}")
    else:
        print("❌ FAILED")
    
    print("=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("WRONG ID TYPE DETECTION TEST")
    print("=" * 70)
    print("\nTesting proper error handling for wrong ID types")
    print("Make sure the API server is running at http://localhost:8000")
    
    try:
        # Test if server is running
        requests.get(f"{BASE_URL}/docs", timeout=2)
        
        test_playlist_id_on_artist_endpoint()
        test_correct_endpoints()
        
        print("\n✅ All tests completed!\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API server.")
        print("Please start the server with: python -m src.main")
        print()
