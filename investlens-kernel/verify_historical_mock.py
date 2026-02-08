
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from pprint import pprint
from datetime import datetime, timedelta

sys.path.append(os.getcwd())

from app.services.providers.alpha_vantage import AlphaVantageProvider

class TestAlphaVantage(unittest.TestCase):
    @patch('app.services.providers.alpha_vantage.requests.get')
    def test_get_historical_structure(self, mock_get):
        # Mock response data matching AV format
        mock_response = {
            "Meta Data": {
                "1. Information": "Daily Prices (open, high, low, close) and Volumes",
                "2. Symbol": "IBM",
                "3. Last Refreshed": "2023-10-27",
                "4. Output Size": "Compact",
                "5. Time Zone": "US/Eastern"
            },
            "Time Series (Daily)": {
                (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"): {
                    "1. open": "142.00",
                    "2. high": "143.00",
                    "3. low": "141.00",
                    "4. close": "142.50",
                    "5. volume": "3000000"
                },
                (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"): {
                    "1. open": "140.00",
                    "2. high": "141.00",
                    "3. low": "139.00",
                    "4. close": "140.50",
                    "5. volume": "3500000"
                }
            }
        }
        
        mock_get.return_value.json.return_value = mock_response
        
        provider = AlphaVantageProvider(api_key="test_key")
        result = provider.get_historical("IBM", period="1mo")
        
        print("\nResult from get_historical:")
        pprint(result)
        
        # Verify it returns a dict, not a list
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn("symbol", result)
        self.assertIn("candles", result)
        self.assertIn("data_source", result)
        self.assertEqual(result["data_source"], "alpha_vantage")
        self.assertEqual(result["symbol"], "IBM")
        self.assertIsInstance(result["candles"], list)
        self.assertEqual(len(result["candles"]), 2)
        
        # Verify first candle structure
        sorted_candles = sorted(result["candles"], key=lambda x: x["date"])
        first_candle = sorted_candles[0] 
        # Check against expected date
        expected_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        self.assertEqual(first_candle["date"], expected_date)
        self.assertEqual(first_candle["close"], 140.50)

if __name__ == '__main__':
    unittest.main()
