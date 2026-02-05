import sys
import os

# Add current dir to path
sys.path.append(os.getcwd())

try:
    from main import app
    print("SUCCESS: main.py imported successfully")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
