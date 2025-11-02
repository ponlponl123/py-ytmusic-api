"""Test the /browse/user/{channelId} endpoint with the problematic channel"""

import requests

BASE_URL = "http://localhost:8000"

def test_user_endpoint():
    """Test with the channel that was causing the musicImmersiveHeaderRenderer error"""
    
    channel_id = "UCZwlNfizEaM-kqPTAQ2ptVg"  # Kobo Kanaeru
    
    print(f"\n🧪 Testing /browse/user/{channel_id}")
    print("=" * 70)
    
    response = requests.get(f"{BASE_URL}/browse/user/{channel_id}", timeout=30)
    
    print(f"Status Code: {response.status_code}", end=" ")
    if response.status_code == 200:
        print("✅ SUCCESS!")
    else:
        print("❌ FAILED")
    
    data = response.json()
    
    if response.status_code == 200:
        print(f"\nResponse structure:")
        print(f"  - message: {data.get('message')}")
        print(f"  - query: {data.get('query')}")
        
        if 'note' in data:
            print(f"  - note: {data.get('note')}")
        
        if 'result' in data:
            result = data['result']
            print(f"\nResult keys: {list(result.keys())}")
            
            if 'name' in result:
                print(f"  - Name: {result['name']}")
            
            if 'channelId' in result:
                print(f"  - Channel ID: {result['channelId']}")
            
            if 'description' in result:
                desc = result['description']
                print(f"  - Description: {desc[:100]}..." if len(desc) > 100 else f"  - Description: {desc}")
            
            if 'views' in result:
                print(f"  - Views: {result['views']}")
            
            if 'subscribers' in result:
                print(f"  - Subscribers: {result['subscribers']}")
            
            if 'songs' in result:
                songs = result['songs']
                print(f"  - Songs section: {type(songs)}")
                if isinstance(songs, dict) and 'browseId' in songs:
                    print(f"    Browse ID: {songs['browseId']}")
            
            if 'albums' in result:
                albums = result['albums']
                print(f"  - Albums section: {type(albums)}")
                if isinstance(albums, dict) and 'browseId' in albums:
                    print(f"    Browse ID: {albums['browseId']}")
    else:
        print(f"\nError response:")
        print(f"  {data}")
    
    print("=" * 70)


def test_artist_endpoint():
    """Test the same channel with the artist endpoint for comparison"""
    
    channel_id = "UCZwlNfizEaM-kqPTAQ2ptVg"  # Kobo Kanaeru
    
    print(f"\n🧪 Testing /browse/artist/{channel_id} (for comparison)")
    print("=" * 70)
    
    response = requests.get(f"{BASE_URL}/browse/artist/{channel_id}", timeout=30)
    
    print(f"Status Code: {response.status_code}", end=" ")
    if response.status_code == 200:
        print("✅ SUCCESS!")
    else:
        print("❌ FAILED")
    
    data = response.json()
    
    if response.status_code == 200:
        if 'result' in data:
            result = data['result']
            print(f"\nResult keys: {list(result.keys())}")
            
            if 'name' in result:
                print(f"  - Name: {result['name']}")
            
            if 'channelId' in result:
                print(f"  - Channel ID: {result['channelId']}")
    
    print("=" * 70)


def test_both_channels():
    """Test both problematic channel IDs"""
    
    channels = [
        ("UCZwlNfizEaM-kqPTAQ2ptVg", "Kobo Kanaeru - user fails, artist works"),
        ("UCz4jhqrCfthF8NnldZeK_rw", "Channel - user works, artist fails"),
    ]
    
    for channel_id, description in channels:
        print(f"\n🧪 Testing {description}")
        print("=" * 70)
        print(f"Channel ID: {channel_id}")
        print("-" * 70)
        
        # Test user endpoint
        print("\n/browse/user endpoint:")
        user_response = requests.get(f"{BASE_URL}/browse/user/{channel_id}", timeout=30)
        print(f"  Status: {user_response.status_code}", end=" ")
        if user_response.status_code == 200:
            print("✅")
            user_data = user_response.json()
            if 'note' in user_data:
                print(f"  Note: {user_data['note']}")
            if 'result' in user_data and 'name' in user_data['result']:
                print(f"  Name: {user_data['result']['name']}")
        else:
            print("❌")
            print(f"  Error: {user_response.json()}")
        
        # Test artist endpoint
        print("\n/browse/artist endpoint:")
        artist_response = requests.get(f"{BASE_URL}/browse/artist/{channel_id}", timeout=30)
        print(f"  Status: {artist_response.status_code}", end=" ")
        if artist_response.status_code == 200:
            print("✅")
            artist_data = artist_response.json()
            if 'note' in artist_data:
                print(f"  Note: {artist_data['note']}")
            if 'result' in artist_data and 'name' in artist_data['result']:
                print(f"  Name: {artist_data['result']['name']}")
        else:
            print("❌")
            print(f"  Error: {artist_response.json()}")
        
        print("=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("USER & ARTIST ENDPOINT CROSS-FALLBACK TEST")
    print("=" * 70)
    print("\nTesting fix for musicImmersiveHeaderRenderer/musicVisualHeaderRenderer issues")
    print("Make sure the API server is running at http://localhost:8000")
    
    try:
        # Test if server is running
        requests.get(f"{BASE_URL}/docs", timeout=2)
        
        test_both_channels()
        
        print("\n✅ All tests completed!\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API server.")
        print("Please start the server with: python -m src.main")
        print()
