
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

print("Checking imports...")

try:
    import openai
    print("✅ openai imported")
except ImportError as e:
    print(f"❌ openai import failed: {e}")

try:
    from duckduckgo_search import DDGS
    print("✅ duckduckgo_search imported")
except ImportError as e:
    print(f"❌ duckduckgo_search import failed: {e}")

try:
    import yfinance as yf
    print("✅ yfinance imported")
except ImportError as e:
    print(f"❌ yfinance import failed: {e}")

try:
    import numpy as np
    print("✅ numpy imported")
except ImportError as e:
    print(f"❌ numpy import failed: {e}")

# Check local modules
try:
    from app.services.asset_search import search
    print("✅ app.services.asset_search imported")
except ImportError as e:
    print(f"❌ app.services.asset_search import failed: {e}")
except Exception as e:
    print(f"❌ app.services.asset_search failed with error: {e}")

try:
    from app.services.market_data import get_quote
    print("✅ app.services.market_data imported")
except ImportError as e:
    print(f"❌ app.services.market_data import failed: {e}")
except Exception as e:
    print(f"❌ app.services.market_data failed with error: {e}")

try:
    from app.services.llm_provider import LLMProvider
    print("✅ app.services.llm_provider imported")
except ImportError as e:
    print(f"❌ app.services.llm_provider import failed: {e}")
except Exception as e:
    print(f"❌ app.services.llm_provider failed with error: {e}")

print("Verification complete.")
