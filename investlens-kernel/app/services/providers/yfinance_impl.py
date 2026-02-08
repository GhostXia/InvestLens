# pyre-ignore[21]: yfinance installed but not found by IDE
import yfinance as yf
import logging
from typing import Dict, Any, Optional
# pyre-ignore[21]: relative import
from .base import BaseDataProvider

logger = logging.getLogger(__name__)

class YFinanceProvider(BaseDataProvider):
    """
    Data provider using yfinance library.
    Acts as the robust fallback or primary for free data.
    """

    def get_quote(self, ticker: str) -> Optional[Dict[str, Any]]:
        try:
            stock = yf.Ticker(ticker)
            # pyre-ignore[16]: fast_info dynamic attribute
            info = stock.fast_info
            
            # Fallback logic similar to original market_data.py
            if not info or not hasattr(info, 'last_price'):
                 standard_info = stock.info
                 if not standard_info or 'currentPrice' not in standard_info:
                     return None
                 
                 price = float(standard_info.get('currentPrice'))
                 previous_close = float(standard_info.get('previousClose')) if standard_info.get('previousClose') else None
                 name = standard_info.get('shortName', ticker)
                 currency = standard_info.get('currency', 'USD')
            else:
                 price = float(info.last_price)
                 previous_close = float(info.previous_close) if info.previous_close else None
                 
                 # Optimization: access info just for name if missing
                 # But stock.info triggers a full request. We might rely on cached mapping?
                 # For now, let's try to get it if we can, or fallback to ticker.
                 # Actually, fast_info doesn't have name.
                 # To support better UI, we should try to get the real name.
                 # We can check if we have it in a lightweight way, or just accept the IO hit.
                 # Given this is "Quant Kernel", correctness is good.
                 try:
                     name = stock.info.get('shortName', stock.info.get('longName', ticker.upper()))
                 except:
                     name = ticker.upper()
                 
                 currency = info.currency

            if previous_close:
                change = price - previous_close
                change_percent = (change / previous_close) * 100
            else:
                change = 0.0
                change_percent = 0.0

            return {
                "symbol": ticker.upper(),
                # pyre-ignore[6]: Rounding float
                "price": round(price, 2),
                # pyre-ignore[6]: Rounding float
                "change": round(change, 2),
                # pyre-ignore[6]: Rounding float
                "change_percent": round(change_percent, 2),
                "name": name,
                "currency": currency
            }
        except Exception as e:
            logger.error(f"YFinance quote failed: {e}")
            return None

    def get_financials(self, ticker: str) -> Dict[str, Any]:
        try:
            stock = yf.Ticker(ticker)
            # Use info instead of financials dataframe, as it has the profile and key summary stats
            info = stock.info
            
            if not info:
                return {}
                
            # Map YF fields to common format (matching AV keys where possible)
            financials = {
                "Description": info.get("longBusinessSummary", "No description available."),
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "FullTimeEmployees": info.get("fullTimeEmployees", "N/A"),
                "MarketCapitalization": info.get("marketCap", "N/A"),
                "EBITDA": info.get("ebitda", "N/A"),
                "PERatio": info.get("trailingPE", "N/A"),
                "PEGRatio": info.get("pegRatio", "N/A"),
                "BookValue": info.get("bookValue", "N/A"),
                "DividendYield": info.get("dividendYield", "N/A"),
                "EPS": info.get("trailingEps", "N/A"),
                "RevenueTTM": info.get("totalRevenue", "N/A"),
                "GrossProfitTTM": info.get("grossProfits", "N/A"), # Note: YF might return raw number
                "ProfitMargin": info.get("profitMargins", "N/A"),
                "OperatingMarginTTM": info.get("operatingMargins", "N/A"),
                "ReturnOnAssetsTTM": info.get("returnOnAssets", "N/A"),
                "ReturnOnEquityTTM": info.get("returnOnEquity", "N/A"),
                "TrailingPE": info.get("trailingPE", "N/A"),
                "ForwardPE": info.get("forwardPE", "N/A"),
                "PriceToSalesRatioTTM": info.get("priceToSalesTrailing12Months", "N/A"),
                "PriceToBookRatio": info.get("priceToBook", "N/A"),
                "Beta": info.get("beta", "N/A"),
                "52WeekHigh": info.get("fiftyTwoWeekHigh", "N/A"),
                "52WeekLow": info.get("fiftyTwoWeekLow", "N/A"),
                "50DayMovingAverage": info.get("fiftyDayAverage", "N/A"),
                "200DayMovingAverage": info.get("twoHundredDayAverage", "N/A"),
                "Website": info.get("website", ""),
            }
            
            # Format large numbers for consistency with AV string format?
            # Or leave as numbers and let frontend handle?
            # Since AV returns strings, frontend will likely expect strings or raw numbers.
            # Best to leave YF numbers as numbers and handle mixed types in frontend formatter.
            
            return financials
        except Exception as e:
            logger.error(f"YFinance financials failed: {e}")
            return {}

    def get_market_context(self) -> Dict[str, str]:
        context = {}
        indices = {
            "SPY": "S&P 500 ETF",
            "^VIX": "Volatility Index"
        }
        
        try:
            for symbol, name in indices.items():
                try:
                    tick = yf.Ticker(symbol)
                    # pyre-ignore[16]: fast_info dynamic attribute
                    info = tick.fast_info
                    if hasattr(info, 'last_price') and hasattr(info, 'previous_close'):
                        price = info.last_price
                        prev = info.previous_close
                        change_pct = ((price - prev) / prev) * 100 if prev else 0.0
                        context[name] = f"{price:.2f} ({change_pct:+.2f}%)"
                except Exception:
                    context[name] = "Data Unavailable"
            return context
        except Exception as e:
            return context
