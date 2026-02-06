import requests

# Test Yahoo Finance Search API
query = "APP"

try:
    print(f"Testing Yahoo Finance Search API for: '{query}'\n")
    
    # Yahoo Finance Search endpoint
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {
        "q": query,
        "quotesCount": 10,
        "newsCount": 0,
        "enableFuzzyQuery": False,
        "quotesQueryId": "tss_match_phrase_query"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, params=params, headers=headers, timeout=5)
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response structure:")
        print(f"Keys: {data.keys()}\n")
        
        if 'quotes' in data:
            quotes = data['quotes']
            print(f"Number of results: {len(quotes)}\n")
            
            print("Sample results:")
            for i, quote in enumerate(quotes[:5], 1):
                print(f"\n{i}. {quote.get('symbol', 'N/A')}")
                print(f"   Name: {quote.get('longname') or quote.get('shortname', 'N/A')}")
                print(f"   Type: {quote.get('quoteType', 'N/A')}")
                print(f"   Exchange: {quote.get('exchange', 'N/A')}")
                print(f"   Score: {quote.get('score', 'N/A')}")
                
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
