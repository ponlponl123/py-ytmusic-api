"""
Test script to verify error handling in the YTMusic API wrapper
"""
import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000"

async def test_health_endpoint():
    """Test the health check endpoint"""
    print("🏥 Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/search/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

async def test_search_with_problematic_query():
    """Test search with a query that might cause KeyError"""
    print("\n🔍 Testing search with potentially problematic query...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/search/search?query=nightcore&limit=5")
            print(f"Status: {response.status_code}")
            result = response.json()
            if "warning" in result:
                print(f"⚠️ Warning: {result['warning']}")
            print("✅ Search successful")
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_invalid_video_id():
    """Test with invalid video ID"""
    print("\n📹 Testing with invalid video ID...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/browse/song/invalid_id")
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                print(f"Error response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

async def test_api_status():
    """Test global API status"""
    print("\n📊 Testing API status...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/status")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

async def test_rate_limiting():
    """Test rate limiting (make rapid requests)"""
    print("\n⚡ Testing rate limiting with rapid requests...")
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                response = await client.get(f"{BASE_URL}/search/search?query=test{i}&limit=1")
                print(f"Request {i+1}: Status {response.status_code}")
                if response.status_code == 429:
                    print("🚦 Rate limiting detected")
                    break
            except Exception as e:
                print(f"Request {i+1} failed: {e}")
            await asyncio.sleep(0.1)  # Small delay between requests

async def main():
    """Run all tests"""
    print("🚀 Starting YTMusic API Error Handling Tests\n")
    
    # Test all endpoints
    await test_api_status()
    await test_health_endpoint()
    await test_search_with_problematic_query()
    await test_invalid_video_id()
    await test_rate_limiting()
    
    print("\n✅ All tests completed!")
    print("\nTo run the API server:")
    print("cd src && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    asyncio.run(main())