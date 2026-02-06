from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseDataProvider(ABC):
    """
    Abstract base class for market data providers.
    Ensures consistent interface across different APIs (YFinance, Alpha Vantage, etc.).
    """

    @abstractmethod
    def get_quote(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch real-time (or delayed) quote for a ticker.
        Returns None if data is unavailable or ticker is invalid.
        
        Expected connection keys:
        - symbol (str)
        - price (float)
        - change (float)
        - change_percent (float)
        - name (str)
        - currency (str)
        """
        pass

    @abstractmethod
    def get_financials(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch key financial metrics (Revenue, Net Income, etc.).
        Returns empty dict if unavailable.
        """
        pass

    @abstractmethod
    def get_market_context(self) -> Dict[str, str]:
        """
        Fetch broad market indicators (e.g., S&P 500, VIX).
        """
        pass
