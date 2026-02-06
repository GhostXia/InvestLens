"""
Market Data Service
===================

This module handles interactions with external market data providers.
Currently utilizes `yfinance` to fetch delayed/real-time equity data.
Also supports AkShare for China A-shares and funds.

Key Responsibilities:
- Fetching current price and change data.
- Normalizing data structures for the frontend.
- Handling API errors and missing tickers.
- Auto-selecting provider based on ticker format.
"""

# pyre-ignore[21]: yfinance installed but not found by IDE
# pyre-ignore[21]: yfinance installed but not found by IDE
import yfinance as yf
import logging
from typing import List, Optional, Any
# pyre-ignore[21]: relative import
from .providers.base import BaseDataProvider
# pyre-ignore[21]: relative import
from .providers.alpha_vantage import AlphaVantageProvider
# pyre-ignore[21]: relative import
from .providers.yfinance_impl import YFinanceProvider
# pyre-ignore[21]: relative import
from .providers.akshare_impl import AkShareProvider
# pyre-ignore[21]: relative import
from .config_manager import config_manager

# Configure logger
logger = logging.getLogger(__name__)

# Initialize Providers
_providers: List[BaseDataProvider] = []
_akshare_provider: Optional[AkShareProvider] = None


def _is_china_ticker(ticker: str) -> bool:
    """
    Check if ticker is a China A-share or fund code.
    A-share codes: 6 digits starting with 0, 3, or 6
    """
    if len(ticker) == 6 and ticker.isdigit():
        return ticker[0] in ('0', '3', '6')
    return False


def reload_providers():
    """
    Re-initializes the provider list based on the configuration manager.
    """
    global _providers, _akshare_provider
    _providers = []
    
    # Load dynamic sources
    sources = config_manager.load_data_sources()
    
    alpha_vantage_added = False
    
    # Add Configured Providers
    for source in sources:
        if not source.get("enabled", True):
            continue
            
        if source["provider_type"] == "alpha_vantage":
            key = source.get("api_key")
            if key:
                _providers.append(AlphaVantageProvider(api_key=key))
                alpha_vantage_added = True

    # Legacy Fallback: If no dynamic AV config, try env var
    if not alpha_vantage_added:
        av_env = AlphaVantageProvider()
        if av_env.api_key:
            _providers.append(av_env)

    # Add YFinance (Always enabled fallback)
    _providers.append(YFinanceProvider())
    
    # Initialize AkShare provider separately (for China market)
    try:
        _akshare_provider = AkShareProvider()
        logger.info("AkShare provider initialized for China market")
    except Exception as e:
        logger.warning(f"AkShare provider failed to initialize: {e}")
        _akshare_provider = None
    
    logger.info(f"Providers reloaded. Active: {[type(p).__name__ for p in _providers]}")

# Initial load
reload_providers()


def get_quote(ticker: str) -> dict:
    """
    Fetches the latest quote using available providers.
    Automatically selects AkShare for China A-share tickers.
    """
    # pyre-ignore[21]: Import exists
    from ..database.models import get_ticker_from_isin
    
    # ISIN Logic
    # pyre-ignore[16]: Pyre string slicing check
    if len(ticker) == 12 and ticker[:2].isalpha():
        converted = get_ticker_from_isin(ticker)
        if converted:
            ticker = converted

    error_details = []
    
    # For China A-share tickers, try AkShare first
    if _is_china_ticker(ticker) and _akshare_provider:
        try:
            quote = _akshare_provider.get_quote(ticker)
            if quote:
                return quote
        except Exception as e:
            error_details.append(f"AkShare: {str(e)}")
    
    # Fall back to standard providers
    for provider in _providers:
        try:
            quote = provider.get_quote(ticker)
            if quote:
                return quote
        except Exception as e:
            error_details.append(f"{type(provider).__name__}: {str(e)}")
            continue

    # If we get here, all providers failed
    logger.error(f"All providers failed for {ticker}: {error_details}")
    return {
        "symbol": str(ticker).upper(),
        "error": "Data Unavailable",
        "details": "; ".join(error_details)
    }

def get_historical_data(ticker: str, period: str = "6mo", interval: str = "1d") -> dict:
    """
    Fetches historical OHLC (Open, High, Low, Close) data for a ticker.
    Uses AkShare for China A-shares, YFinance for others.
    
    Args:
        ticker (str): The symbol to look up (e.g. NVDA or 000001).
        period (str): The data duration (e.g. '1mo', '1y', 'ytd').
        interval (str): The data granularity (e.g. '1d', '1wk').
        
    Returns:
        dict: A dictionary containing the 'symbol' and a list of 'candles'.
    """
    # For China A-share tickers, try AkShare first
    if _is_china_ticker(ticker) and _akshare_provider:
        try:
            # Map period to our format
            period_map = {
                "1mo": "1m", "3mo": "3m", "6mo": "6m",
                "1y": "1y", "ytd": "1y", "max": "2y"
            }
            ak_period = period_map.get(period, "1y")
            
            candles = _akshare_provider.get_historical(ticker, ak_period)
            if candles:
                return {
                    "symbol": ticker.upper(),
                    "period": period,
                    "interval": interval,
                    "candles": candles,
                    "data_source": "akshare"
                }
        except Exception as e:
            logger.warning(f"AkShare historical failed for {ticker}: {e}")

    # Try Configured Providers (e.g., AlphaVantage)
    # This enables custom data sources for historical charts
    for provider in _providers:
        # Skip standard YFinanceProvider here as we have specific fallback logic below
        # or if it doesn't implement get_historical
        if hasattr(provider, 'get_historical'):
            try:
                # pyre-ignore[16]: dynamic attribute
                data = provider.get_historical(ticker, period=period)
                if data:
                    # Enrich with source info if not present
                    if "data_source" not in data:
                        data["data_source"] = "custom"
                    return data
            except Exception as e:
                logger.warning(f"Provider {type(provider).__name__} history failed: {e}")
    
    # Fall back to YFinance
    try:
        # Normalize ticker for YFinance if needed (especially for A-shares fallback)
        yf_ticker = ticker
        if len(ticker) == 6 and ticker.isdigit():
            # Shanghai: 6xxxxx (A-Share/KC), 9xxxxx (B-Share), 5xxxxx (ETF/Fund)
            if ticker.startswith(('5', '6', '9')):
                yf_ticker = f"{ticker}.SS"
            # Shenzhen: 0xxxxx (A-Share), 3xxxxx (ChiNext), 2xxxxx (B-Share), 1xxxxx (ETF/Fund)
            elif ticker.startswith(('0', '1', '2', '3')):
                yf_ticker = f"{ticker}.SZ"
            # Beijing: 8xxxxx, 4xxxxx (Often .BJ but Yahoo support varies)
        
        stock = yf.Ticker(yf_ticker)
        hist = stock.history(period=period, interval=interval, auto_adjust=True)
        
        if hist.empty:
            return {"error": f"No historical data found for {ticker}"}
            
        candles = []
        for date, row in hist.iterrows():
            candles.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })
            
        return {
            "symbol": ticker.upper(),
            "period": period,
            "interval": interval,
            "candles": candles,
            "data_source": "yfinance"
        }
    except Exception as e:
        return {"error": str(e)}

# pyre-ignore[21]: numpy installed but not found by IDE
import numpy as np
from datetime import datetime, timedelta

def get_prediction(ticker: str, days: int = 7) -> dict:
    """
    Generates a stochastic price prediction using Monte Carlo simulation.
    Warning: This is a statistical projection, not financial advice.
    
    Args:
        ticker (str): Asset symbol.
        days (int): Number of days to forecast.
        
    Returns:
        dict: Prediction data points with confidence intervals.
    """
    try:
        # 1. Get recent history (past 30 days) for volatility
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo", interval="1d")
        
        if hist.empty:
            return {"error": "Insufficient data"}
            
        returns = hist['Close'].pct_change().dropna()
        if len(returns) < 2:
             return {"error": "Not enough data"}

        daily_volatility = returns.std()
        last_price = hist['Close'].iloc[-1]
        # Ensure we have a valid datetime
        last_date = hist.index[-1]
        # Handle pandas Timestamp vs python datetime
        if hasattr(last_date, 'to_pydatetime'):
            last_date = last_date.to_pydatetime()
        
        predictions = []
        z_score = 1.96 
        current_price = last_price
        
        for i in range(1, days + 1):
            next_date = last_date + timedelta(days=i)
            drift = 0.0005 
            uncertainty = current_price * daily_volatility * np.sqrt(i) * z_score
            random_shock = np.random.normal(0, daily_volatility)
            
            # Markov chain step
            predicted_close = current_price * (1 + drift + random_shock)
            current_price = predicted_close
            
            predictions.append({
                "date": next_date.strftime("%Y-%m-%d"),
                "price": round(predicted_close, 2),
                "upper": round(last_price * (1 + i*drift) + uncertainty, 2),
                "lower": round(last_price * (1 + i*drift) - uncertainty, 2)
            })
            
        return {
            "symbol": ticker.upper(),
            "forecast_days": days,
            "volatility_context": round(daily_volatility * 100, 2),
            "predictions": predictions
        }
    except Exception as e:
        return {"error": str(e)}

def get_financials(ticker: str) -> dict:
    """
    Fetches key financial metrics using available providers.
    """
    for provider in _providers:
        try:
            data = provider.get_financials(ticker)
            if data:
                return data
        except Exception:
            continue
    return {}

def get_market_context() -> dict:
    """
    Fetches broad market indicators.
    """
    # For context, we can try to merge logic or just take the first success.
    # YFinance is specifically good for this (VIX, etc), AV might be limited.
    # We'll try all, but YFinance implemented it well.
    for provider in _providers:
        try:
            context = provider.get_market_context()
            if context and "Data Unavailable" not in str(context.values()):
                 # Heuristic: if we got real data, return it
                 return context
        except Exception:
            continue
            
    # Fallback if preferred providers failed, try to return whatever we got
    # (Or just return empty to fail gracefully)
    return {}
