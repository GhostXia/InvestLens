# pyre-ignore[21]: requests installed but not found
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_config_lifecycle():
    logger.info("Starting Dynamic Config Verification...")
    
    # 1. Get initial sources
    try:
        response = requests.get(f"{BASE_URL}/config/sources")
        if response.status_code != 200:
            logger.error(f"Failed to fetch sources: {response.text}")
            return
        
        initial_sources = response.json()
        logger.info(f"Initial sources: {len(initial_sources)}")
    except Exception as e:
        logger.error(f"Failed to connect to backend: {e}")
        return

    # 2. Add a new Alpha Vantage source
    new_source = {
        "name": "Test AV Provider",
        "provider_type": "alpha_vantage",
        "api_key": "TEST_KEY_123", # Dummy key
        "endpoint_override": "",
        "enabled": True
    }
    
    payload = {
        "sources": initial_sources + [new_source]
    }
    
    logger.info("Adding new source...")
    try:
        response = requests.post(f"{BASE_URL}/config/sources", json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to save sources: {response.text}")
            return
        logger.info("Sources saved successfully.")
    except Exception as e:
        logger.error(f"Failed to post sources: {e}")
        return
        
    # 3. Verify it was added
    response = requests.get(f"{BASE_URL}/config/sources")
    updated_sources = response.json()
    found = any(s["api_key"] == "TEST_KEY_123" for s in updated_sources)
    
    if found:
        logger.info("SUCCESS: New source persisted.")
    else:
        logger.error("FAILURE: New source not found in fetched list.")
        
    # 4. Cleanup (optional, remove the test source)
    cleanup_payload = {
        "sources": [s for s in updated_sources if s["api_key"] != "TEST_KEY_123"]
    }
    requests.post(f"{BASE_URL}/config/sources", json=cleanup_payload)
    logger.info("Cleanup completed.")

if __name__ == "__main__":
    test_config_lifecycle()
