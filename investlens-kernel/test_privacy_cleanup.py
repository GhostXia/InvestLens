# pyre-ignore[21]: requests installed but not found
import requests
import os

API_BASE = "http://localhost:8000"

def test_privacy_cleanup():
    """Test the privacy data cleanup feature"""
    
    print("=== Privacy Cleanup Feature Test ===\n")
    
    # 1. Check initial status
    print("[1/5] Checking initial privacy data status...")
    response = requests.get(f"{API_BASE}/privacy/status")
    if response.ok:
        status = response.json()
        print(f"  Config dir exists: {status['config_dir_exists']}")
        print(f"  Sources config exists: {status['sources_config_exists']}")
    else:
        print("  ❌ Failed to get status")
        return
    
    # 2. Create test data source config
    print("\n[2/5] Creating test data source configuration...")
    test_source = {
        "sources": [{
            "name": "Test Alpha Vantage",
            "provider_type": "alpha_vantage",
            "api_key": "TEST_KEY_12345",
            "endpoint_override": "",
            "enabled": True
        }]
    }
    
    response = requests.post(f"{API_BASE}/config/sources", json=test_source)
    if response.ok:
        print("  ✓ Test configuration created")
    else:
        print("  ❌ Failed to create test config")
        return
    
    # 3. Verify config was created
    print("\n[3/5] Verifying configuration was saved...")
    response = requests.get(f"{API_BASE}/privacy/status")
    if response.ok:
        status = response.json()
        if status['sources_config_exists']:
            print("  ✓ Configuration file exists")
        else:
            print("  ❌ Configuration file not found")
            return
    
    # 4. Clear all privacy data
    print("\n[4/5] Clearing all privacy data...")
    response = requests.post(f"{API_BASE}/privacy/clear-all")
    if response.ok:
        result = response.json()
        print(f"  ✓ Cleanup successful")
        print(f"  Details: {result['details']}")
    else:
        print(f"  ❌ Cleanup failed: {response.text}")
        return
    
    # 5. Verify data was cleared
    print("\n[5/5] Verifying data was cleared...")
    response = requests.get(f"{API_BASE}/privacy/status")
    if response.ok:
        status = response.json()
        if not status['sources_config_exists']:
            print("  ✓ Configuration file successfully deleted")
        else:
            print("  ❌ Configuration file still exists")
            return
    
    print("\n=== ✅ All tests passed! ===")

if __name__ == "__main__":
    test_privacy_cleanup()
