
import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Add project root to path
sys.path.append(os.getcwd())

from app.services import market_data
from app.services import consensus
from app.services.llm_provider import llm_client

# Mock the LLM to avoid API calls and just inspect the prompt if possible,
# Or just run it and see if it crashes.
# For this verify script, we'll just run it and check if the prompt building worked.
# We can't easily inspect the local variable 'user_prompt' inside the function without modifying code,
# so we will check if the new data fetching functions return valid data first.

print("--- Testing Market Data Functions ---")
print("1. Testing get_financials('AAPL')...")
fin = market_data.get_financials('AAPL')
print(f"Result: {fin}")
if not fin:
    print("⚠️ Warning: No financials returned (could be network or yfinance issue)")
else:
    print("✅ Financials returned")

print("\n2. Testing get_market_context()...")
macro = market_data.get_market_context()
print(f"Result: {macro}")
if not macro:
    print("⚠️ Warning: No macro context returned")
else:
    print("✅ Macro context returned")

print("\n--- Testing Consensus Flow (Mock LLM) ---")
# We will rely on llm_provider's mock fallback if no API key is present,
# or we can force it.
# Let's try to run a generation and catch any exceptions.

try:
    # Use a dummy key to assume we might hit the API, but if it fails it falls back.
    # Actually, we want to ensure the code *before* the API call works (data fetching).
    response = consensus.generate_consensus_analysis("AAPL", ["Fundamental"], api_key="test")
    print("\n✅ Consensus Analysis ran without crashing.")
    print("Summary Snapshot:")
    print(response.summary[:100] + "...")
except Exception as e:
    print(f"\n❌ Consensus Analysis Failed: {e}")
    import traceback
    traceback.print_exc()
