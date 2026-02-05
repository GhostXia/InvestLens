
import sys
import os
import logging

# Add current dir to path
sys.path.append(os.getcwd())

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

from app.services.search_service import search_web

def test_search():
    print("Starting search test...")
    results = search_web("Apple stock news", max_results=3)
    if results:
        print("Successfully fetched search results:")
        for r in results:
            print(f"- {r['title']} ({r['link']})")
    else:
        print("No results returned or search failed.")

if __name__ == "__main__":
    test_search()
