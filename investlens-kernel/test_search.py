
import logging
from app.services.search_service import search_web

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search():
    ticker = "NVDA"
    print(f"Fetching news for: {ticker}")
    results = search_web("", max_results=5, ticker=ticker)
    
    if results:
        print(f"\n✅ Success! Found {len(results)} news items:")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['title']}")
            print(f"   Link: {r['link']}")
    else:
        print("\n❌ No news found.")

if __name__ == "__main__":
    test_search()
