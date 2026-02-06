# pyre-ignore[21]: requests installed but not found
import requests

API_BASE = "http://localhost:8000"

def test_search_endpoints():
    """Test DuckDuckGo search API endpoints"""
    
    print("=== DuckDuckGo Search API Tests ===\n")
    
    # 1. Text Search
    print("[1/4] Testing text search...")
    try:
        response = requests.get(f"{API_BASE}/search/text", params={
            "query": "Python编程",
            "max_results": 5
        })
        if response.ok:
            data = response.json()
            print(f"  ✓ Found {data['count']} results")
            if data['results']:
                print(f"  First result: {data['results'][0].get('title', 'N/A')}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # 2. News Search
    print("\n[2/4] Testing news search...")
    try:
        response = requests.get(f"{API_BASE}/search/news", params={
            "query": "科技",
            "max_results": 5
        })
        if response.ok:
            data = response.json()
            print(f"  ✓ Found {data['count']} news items")
            if data['results']:
                print(f"  First news: {data['results'][0].get('title', 'N/A')}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # 3. Search Suggestions
    print("\n[3/4] Testing search suggestions...")
    try:
        response = requests.get(f"{API_BASE}/search/suggestions", params={
            "query": "投资"
        })
        if response.ok:
            data = response.json()
            print(f"  ✓ Found {data['count']} suggestions")
            if data['suggestions']:
                print(f"  Suggestions: {', '.join(data['suggestions'][:3])}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # 4. Image Search
    print("\n[4/4] Testing image search...")
    try:
        response = requests.get(f"{API_BASE}/search/images", params={
            "query": "股票图表",
            "max_results": 5
        })
        if response.ok:
            data = response.json()
            print(f"  ✓ Found {data['count']} images")
            if data['results']:
                print(f"  First image: {data['results'][0].get('title', 'N/A')}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n=== Tests Complete! ===")
    print("\n提示：如果测试失败，请确保后端服务器正在运行：")
    print("  python -m uvicorn main:app --reload --port 8000")

if __name__ == "__main__":
    test_search_endpoints()
