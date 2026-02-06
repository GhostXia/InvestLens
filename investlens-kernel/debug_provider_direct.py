
import logging
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.append(os.getcwd())

# Setup logging to see the DEBUG prints I added
logging.basicConfig(level=logging.DEBUG)

from app.services.providers.akshare_impl import AkShareProvider


def test_name_resolution():
    with open("debug_log.txt", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            f.write(msg + "\n")
            f.flush()
            
        log("Initialize AkShareProvider...")
        try:
            provider = AkShareProvider()
        except Exception as e:
            log(f"Failed to init provider: {e}")
            import traceback
            f.write(traceback.format_exc())
            return

        ticker = "603986" # Raw code
        log(f"\n--- Testing get_name('{ticker}') ---")
        
        try:
            name = provider.get_name(ticker)
            log(f"\nResult Name: {name}")
            
            if name == '兆易创新':
                log("\nSUCCESS: Name is correct.")
            else:
                log(f"\nFAILURE: Name is '{name}' (Expected '兆易创新')")
                
        except Exception as e:
            log(f"\nEXCEPTION during get_name: {e}")
            import traceback
            f.write(traceback.format_exc())

if __name__ == "__main__":
    test_name_resolution()
