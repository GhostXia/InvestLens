"""
Test duckduckgo-search library without site: restriction
to see what information is available for Chinese funds
"""
from duckduckgo_search import DDGS

query = "大成中国灵活配置基金"

print(f"Testing DDGS text search for: '{query}'\n")

try:
    ddgs = DDGS()
    
    # Use text search (web search)
    results = ddgs.text(query, max_results=5)
    
    print(f"Found {len(results)} results:\n")
    
    for i, r in enumerate(results, 1):
        print(f"{i}. {r.get('title', 'N/A')}")
        print(f"   URL: {r.get('href', 'N/A')}")
        print(f"   Body: {r.get('body', 'N/A')[:150]}...")
        print()
        
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
