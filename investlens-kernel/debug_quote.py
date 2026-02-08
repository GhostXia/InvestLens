
import sys
import os

# Add the current directory to path so we can import 'app'
# Assuming we run this from inside 'investlens-kernel'
sys.path.append(os.getcwd())

from app.services import market_data
print(market_data.get_quote('BTC-USD'))
