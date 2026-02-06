import os
import sys
import asyncio
from dotenv import load_dotenv

# Ensure we can import from app
sys.path.append(os.getcwd())

load_dotenv()

from app.services import consensus
# pyre-ignore[21]: Imports exist
from app.services.llm_provider import llm_client

# Setup logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_consensus():
    ticker = "600519" # Moutai
    print(f"--- Starting Consensus Test for {ticker} ---")
    
    try:
        # Mock LLM response to save tokens/time if needed, but we want to test real flow if possible.
        # However, let's assume we want to see the LOGS primarily.
        
        # If no API key, it will use mock.
        # We can check if API key exists.
        if not os.getenv("LLM_API_KEY"):
            print("WARNING: No LLM_API_KEY found, using Mock Fallback.")
            
        result = consensus.generate_consensus_analysis(
            ticker=ticker,
            focus_areas=["Growth", "Risk"],
            quant_mode=True # Test the high risk plan injection too
        )
        
        print("\n=== FINAL RESULT ===")
        print(f"Score: {result.confidence_score}")
        print(f"Summary: {result.summary[:100]}...")
        print(f"Bull: {result.bullish_case[:50]}...")
        print(f"Bear: {result.bearish_case[:50]}...")
        print(f"Sentiment/Plan: {result.sentiment_analysis[:50]}...")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_consensus()
