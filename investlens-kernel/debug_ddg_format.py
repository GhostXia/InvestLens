from duckduckgo_search import DDGS
import json

query = "APP"

try:
    print(f"Testing DuckDuckGo suggestions for: '{query}'")
    
    with DDGS() as ddgs:
        suggestions = ddgs.suggestions(query)
        
        print(f"\nType of suggestions: {type(suggestions)}")
        print(f"\nRaw suggestions output:")
        print(suggestions)
        
        # Try to iterate
        print(f"\nIterating over suggestions:")
        suggestion_list = list(suggestions)
        print(f"Number of suggestions: {len(suggestion_list)}")
        
        for i, s in enumerate(suggestion_list):
            print(f"\nSuggestion {i+1}:")
            print(f"  Type: {type(s)}")
            print(f"  Content: {s}")
            if isinstance(s, dict):
                print(f"  Keys: {s.keys()}")
                
except Exception as e:
    print(f"\nError occurred: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
