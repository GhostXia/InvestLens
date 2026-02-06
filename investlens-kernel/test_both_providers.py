import requests
import json

def test_provider(provider_name):
    print(f"\n{'='*60}")
    print(f"Testing {provider_name.upper()} Provider")
    print(f"{'='*60}\n")
    
    try:
        url = f"http://localhost:8000/search/suggestions?query=APP&provider={provider_name}"
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nQuery: {data.get('query')}")
            print(f"Provider: {data.get('provider')}")
            print(f"Count: {data.get('count')}\n")
            
            suggestions = data.get('suggestions', [])
            print("Suggestions:")
            for i, s in enumerate(suggestions[:5], 1):
                print(f"\n{i}. {s.get('ticker', 'N/A')}")
                print(f"   Name: {s.get('name', 'N/A')}")
                if 'exchange' in s:
                    print(f"   Exchange: {s.get('exchange')}")
                if 'asset_type' in s:
                    print(f"   Type: {s.get('asset_type')}")
                if 'isDdg' in s:
                    print(f"   Source: DuckDuckGo")
                if 'isYahoo' in s:
                    print(f"   Source: Yahoo Finance")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

# Test both providers
test_provider("duckduckgo")
test_provider("yahoo")

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print("✓ DuckDuckGo: General search suggestions")
print("✓ Yahoo Finance: Financial ticker suggestions")
