
import sys
import os

# Add local directory to path to find app module
sys.path.append(os.getcwd())

from app.services import market_data
print(market_data.get_quote('BTC-USD'))
