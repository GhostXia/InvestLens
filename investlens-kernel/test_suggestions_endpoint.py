import requests
import json

try:
    response = requests.get("http://localhost:8000/search/suggestions?query=APP")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Error: {e}")
