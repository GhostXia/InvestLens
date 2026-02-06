
import sys
import os
import asyncio
from datetime import datetime

# Add app to path
sys.path.append(os.getcwd())

# Mock environment if needed
# os.environ["ALPHAVANTAGE_API_KEY"] = "..." 

from app.services import market_data
from app.services.config_manager import config_manager

# Force reload to pick up config
market_data.reload_providers()

def test_ticker():
    ticker = "603986"
    print(f"--- Testing Quote for {ticker} ---")
    quote = market_data.get_quote(ticker)
    print(f"Result: {quote}")
    
    print(f"\n--- Testing History for {ticker} ---")
    hist = market_data.get_historical_data(ticker, period="1mo")
    
    print(f"\n--- Testing Fundamentals for {ticker} ---")
    fund = market_data.get_financials(ticker)
    print(f"Fundamentals Keys: {list(fund.keys())}")
    print(f"Sector: {fund.get('Sector')}")
    print(f"RevenueTTM: {fund.get('RevenueTTM')}")
    
    if "candles" in hist:
        print(f"History Source: {hist.get('data_source')}")
        print(f"First candle: {hist['candles'][0]}")
        print(f"Last candle: {hist['candles'][-1]}")
    else:
        print(f"History Error: {hist}")

if __name__ == "__main__":
    test_ticker()
