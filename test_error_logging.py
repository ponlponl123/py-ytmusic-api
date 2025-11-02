"""
Test script to verify improved error logging behavior
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_client_error_logging():
    """Test that client errors (4xx) are logged at INFO level"""
    print("Testing error logging improvements...\n")
    
    # Test 1: Playlist ID on artist endpoint (should be INFO, not ERROR)
    print("1. Testing playlist ID on artist endpoint...")
    playlist_id = "VLPLR48NTfP0M0OtpJgD2obWAuQF8yk0_F77"
    response = requests.get(f"{BASE_URL}/browse/artist/{playlist_id}")
    
    if response.status_code == 400:
        print(f"   ✓ Correctly returned 400 Bad Request")
        data = response.json()
        if "recommendation" in str(data):
            print(f"   ✓ Helpful error message included")
            print(f"   Response: {data['detail']}")
        time.sleep(0.5)
    else:
        print(f"   ✗ Unexpected status code: {response.status_code}")
    
    print()
    
    # Test 2: Playlist ID on user endpoint (should be INFO, not ERROR)
    print("2. Testing playlist ID on user endpoint...")
    response = requests.get(f"{BASE_URL}/browse/user/{playlist_id}")
    
    if response.status_code == 400:
        print(f"   ✓ Correctly returned 400 Bad Request")
        data = response.json()
        if "recommendation" in str(data):
            print(f"   ✓ Helpful error message included")
        time.sleep(0.5)
    else:
        print(f"   ✗ Unexpected status code: {response.status_code}")
    
    print()
    
    # Test 3: Invalid search query (validation error should be INFO)
    print("3. Testing validation error...")
    response = requests.get(f"{BASE_URL}/search?query=test&filter=invalid_filter")
    
    if response.status_code in [400, 422]:
        print(f"   ✓ Correctly returned {response.status_code}")
        time.sleep(0.5)
    else:
        print(f"   ✗ Unexpected status code: {response.status_code}")
    
    print()
    
    # Test 4: Valid request (should be INFO for normal operations)
    print("4. Testing valid request...")
    response = requests.get(f"{BASE_URL}/search?query=test&limit=1")
    
    if response.status_code == 200:
        print(f"   ✓ Successfully returned 200 OK")
    else:
        print(f"   ✗ Unexpected status code: {response.status_code}")
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)
    print("\nCheck the logs:")
    print("  - INFO level: Should show all 4 test requests")
    print("  - ERROR level: Should be empty (no server errors)")
    print("\nCommands to check logs:")
    print("  python view_logs.py view 10  # View last 10 log entries")
    print("  python view_logs.py errors   # Should show no errors")
    print("  python view_logs.py stats    # View log statistics")


if __name__ == "__main__":
    try:
        test_client_error_logging()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server")
        print("Please start the server first:")
        print("  python -m src.main")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
