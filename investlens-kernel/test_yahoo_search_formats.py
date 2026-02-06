"""
Test Yahoo Finance search with different query formats
"""
import requests
import json

def test_search(query):
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    try:
        r = requests.get(
            'https://query2.finance.yahoo.com/v1/finance/search',
            params={'q': query, 'quotesCount': 10, 'newsCount': 0},
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        data = r.json()
        
        quotes = data.get('quotes', [])
        print(f"Found {len(quotes)} results:")
        
        for i, q in enumerate(quotes[:5], 1):
            print(f"\n{i}. {q.get('symbol', 'N/A')}")
            print(f"   Name: {q.get('longname') or q.get('shortname', 'N/A')}")
            print(f"   Type: {q.get('quoteType', 'N/A')}")
            print(f"   Exchange: {q.get('exchange', 'N/A')}")
            
    except Exception as e:
        print(f"Error: {e}")

# Test different query formats
test_search("大成中国灵活配置基金")  # Simplified Chinese
test_search("大成中國靈活配置基金")  # Traditional Chinese (approximation)
test_search("HK0000181112")          # ISIN code
test_search("Dacheng China")         # English name
test_search("0P00011W8C.HK")         # Yahoo ticker (from previous result)
