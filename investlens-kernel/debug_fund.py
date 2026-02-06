
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

from app.services.providers.akshare_impl import AkShareProvider

def test_fund():
    print("Initializing AkShareProvider...")
    provider = AkShareProvider()
    ticker = "008163"
    
    print(f"\n--- Testing get_quote('{ticker}') ---")
    quote = provider.get_quote(ticker)
    print(f"Result: {quote}")
    
    print(f"\n--- Testing get_historical('{ticker}') ---")
    hist = provider.get_historical(ticker, period="1mo")
    if hist:
        print(f"Result: Found {len(hist)} records")
        print(f"Sample: {hist[0]}")
    else:
        print("Result: None")

if __name__ == "__main__":
    test_fund()
