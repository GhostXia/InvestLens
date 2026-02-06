# pyre-ignore[21]: requests installed but not found by IDE
import requests
import logging
import os
from typing import Dict, Any, Optional, List
# pyre-ignore[21]: relative import
from .base import BaseDataProvider

logger = logging.getLogger(__name__)

class AlphaVantageProvider(BaseDataProvider):
    """
    Data provider using Alpha Vantage API.
    Requires ALPHAVANTAGE_API_KEY env var.
    """
    
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key if api_key else os.getenv("ALPHAVANTAGE_API_KEY")
        if not self.api_key:
            logger.warning("ALPHAVANTAGE_API_KEY not found. Provider disabled.")

    def get_quote(self, ticker: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None

        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": ticker,
                "apikey": self.api_key
            }
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            data = response.json()
            
            quote = data.get("Global Quote", {})
            if not quote:
                return None

            return {
                "symbol": quote.get("01. symbol"),
                "price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": float(quote.get("10. change percent", "0").replace("%", "")),
                "name": ticker.upper(), # AV doesn't return name in Global Quote
                "currency": "USD" # default assumption for AV US stocks
            }
        except Exception as e:
            logger.error(f"Alpha Vantage quote failed: {e}")
            return None

    def get_financials(self, ticker: str) -> Dict[str, str]:
        if not self.api_key:
            return {}

        try:
            params = {
                "function": "OVERVIEW",
                "symbol": ticker,
                "apikey": self.api_key
            }
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            data = response.json()
            
            if not data or "Symbol" not in data:
                return {}

            # Map AV fields to our common format
            financials = {}
            if "RevenueTTM" in data:
                 val = float(data["RevenueTTM"])
                 financials["Total Revenue"] = f"{val/1_000_000_000:.2f}B" if val > 1e9 else str(val)
            
            if "GrossProfitTTM" in data:
                 val = float(data["GrossProfitTTM"])
                 financials["Gross Profit"] = f"{val/1_000_000_000:.2f}B" if val > 1e9 else str(val)

            if "PERatio" in data:
                financials["PE Ratio"] = data["PERatio"]
                
            return financials
        except Exception as e:
            logger.error(f"Alpha Vantage financials failed: {e}")
            return {}

    def get_market_context(self) -> Dict[str, str]:
        # Alpha Vantage requires separate calls for indices, often needs different function
        # For simplicity, we might skip implementation here or use minimal endpoints
        return {}

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for assets using SYMBOL_SEARCH endpoint.
        """
        if not self.api_key:
            return []

        try:
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": query,
                "apikey": self.api_key
            }
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            data = response.json()
            
            matches = data.get("bestMatches", [])
            results = []
            
            for match in matches:
                # AV returns keys like "1. symbol", "2. name", etc.
                symbol = match.get("1. symbol")
                name = match.get("2. name")
                type_ = match.get("3. type")
                region = match.get("4. region")
                
                if symbol:
                    results.append({
                        "ticker": symbol,
                        "name": name or symbol,
                        "exchange": region or "US",
                        "asset_type": type_ or "Stock",
                        "isCustom": True,  # Mark as custom/AV
                        "source": "AlphaVantage"
                    })
            
            return results
        except Exception as e:
            logger.error(f"Alpha Vantage search failed: {e}")
            return []

    def get_historical(self, ticker: str, period: str = "1y") -> Optional[List[Dict[str, Any]]]:
        """
        Fetch historical data using TIME_SERIES_DAILY_ADJUSTED.
        """
        if not self.api_key:
            return None

        try:
            # Determine outputsize based on period
            outputsize = "compact" # returns 100 data points (approx 5 months)
            if period in ["6m", "1y", "2y", "max", "ytd"]:
                 outputsize = "full" # returns 20+ years

            params = {
                "function": "TIME_SERIES_DAILY", # Using Daily (Adjusted requires premium sometimes, stick to basic Daily or Adjusted if avail)
                # Actually TIME_SERIES_DAILY_ADJUSTED is standard. Let's try that. 
                # Note: Free tier has limits. TIME_SERIES_DAILY might be safer API-wise but lacks split handling.
                # Let's use TIME_SERIES_DAILY for stability on free tier unless we know otherwise.
                "symbol": ticker,
                "outputsize": outputsize,
                "apikey": self.api_key
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            data = response.json()
            
            # Key is usually "Time Series (Daily)"
            timeseries = data.get("Time Series (Daily)")
            if not timeseries:
                logger.warning(f"Alpha Vantage no historical data for {ticker}: {data.get('Note', 'Unknown error')}")
                return None
                
            candles = []
            # Calculate cutoff date
            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(days=365)
            if period == "1m": cutoff = datetime.now() - timedelta(days=30)
            elif period == "3m": cutoff = datetime.now() - timedelta(days=90)
            elif period == "6m": cutoff = datetime.now() - timedelta(days=180)
            elif period == "2y": cutoff = datetime.now() - timedelta(days=730)
            
            for date_str, values in timeseries.items():
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if dt < cutoff:
                    continue
                    
                candles.append({
                    "date": date_str,
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "volume": int(values.get("5. volume", 0))
                })
            
            # AV returns newest first, we usually want oldest first for charts?
            # Or depends on frontend. Highcharts usually handles it but sorting is safer.
            candles.sort(key=lambda x: x["date"])
            
            return candles

        except Exception as e:
            logger.error(f"Alpha Vantage historical failed: {e}")
            return None
