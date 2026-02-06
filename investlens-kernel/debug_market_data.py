
import logging
import sys
import os

sys.path.append(os.getcwd())
logging.basicConfig(level=logging.ERROR)

from app.services import market_data

def test_market_data_patching():
    print("--- Testing market_data.get_quote('603986.SS') with Patching ---")
    
    # This should trigger YFinance (or fallback) but THEN patch the name
    quote = market_data.get_quote("603986.SS")
    
    print("\nFinal Quote Result:")
    print(quote)
    
    expected_name = '兆易创新'
    actual_name = quote.get('name')
    
    if actual_name == expected_name:
        print(f"\nSUCCESS: Name patched correctly to '{actual_name}'")
    else:
        print(f"\nFAILURE: Name is '{actual_name}' (Expected '{expected_name}')")

if __name__ == "__main__":
    test_market_data_patching()
