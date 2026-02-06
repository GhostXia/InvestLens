"""
Market Data Service
===================

This module handles interactions with external market data providers.
Currently utilizes `yfinance` to fetch delayed/real-time equity data.

Key Responsibilities:
- Fetching current price and change data.
- Normalizing data structures for the frontend.
- Handling API errors and missing tickers.
"""

# pyre-ignore[21]: yfinance installed but not found by IDE
import yfinance as yf
import logging

# Configure logger
logger = logging.getLogger(__name__)

def get_quote(ticker: str) -> dict:
    """
    Fetches the latest quote for a given ticker symbol or ISIN code.

    Args:
        ticker (str): The stock symbol (e.g., 'AAPL', 'NVDA') or ISIN code (e.g., 'HK0000181112').

    Returns:
        dict: A dictionary containing:
            - symbol (str): The uppercase ticker.
            - price (float): Current market price.
            - change (float): Price change (absolute).
            - change_percent (float): Price change (percentage).
            - volume (int): Trading volume.
            - name (str): Short name of the asset.
            - currency (str): Currency code (e.g., 'USD').
    
    Raises:
        ValueError: If the ticker is invalid or no data is found.
    """
    # pyre-ignore[21]: Import exists
    from ..database.models import get_ticker_from_isin
    
    original_input = ticker
    
    # Try to convert ISIN to ticker if needed
    # pyre-ignore[16]: Pyre string slicing check
    if len(ticker) == 12 and ticker[:2].isalpha():  # Looks like an ISIN
        logger.info(f"Detected potential ISIN: {ticker}")
        converted_ticker = get_ticker_from_isin(ticker)
        if converted_ticker:
            logger.info(f"Converted ISIN {ticker} to ticker {converted_ticker}")
            ticker = converted_ticker
        else:
            logger.warning(f"ISIN {ticker} not found in database, trying as-is")
    
    try:
        # Create Ticker object
        stock = yf.Ticker(ticker)
        
        # Fast info fetch (more reliable for real-time than .info)
        info = stock.fast_info
        
        if not info or not hasattr(info, 'last_price'):
             # Fallback to standard info if fast_info fails
             standard_info = stock.info
             if not standard_info or 'currentPrice' not in standard_info:
                 raise ValueError(f"No data found for ticker: {ticker}")
             
             price = float(standard_info.get('currentPrice'))
             previous_close = float(standard_info.get('previousClose')) if standard_info.get('previousClose') else None
             name = standard_info.get('shortName', ticker)
             currency = standard_info.get('currency', 'USD')
        else:
             price = float(info.last_price)
             previous_close = float(info.previous_close) if info.previous_close else None
             # Note: fast_info handling of name/currency varies, minimal fallback here
             name = ticker.upper() 
             currency = info.currency
             
             # Lazy load standard info for extended stats if needed (PE, expensive)
             # For MVP speed, we might leave PE as None if fast_info works
             standard_info = {} # Fallback placeholder

        # Calculate changes
        # Guard against division by zero or missing previous close
        if previous_close:
            change = price - previous_close
            change_percent = (change / previous_close) * 100
        else:
            change = 0.0
            change_percent = 0.0

        return {
            "symbol": ticker.upper(),
            # pyre-ignore[6]: Rounding float is valid
            "price": round(price, 2),
            # pyre-ignore[6]: Rounding float is valid
            "change": round(change, 2),
            # pyre-ignore[6]: Rounding float is valid
            "change_percent": round(change_percent, 2),
            "name": name,
            "currency": currency,
            "volume": (info.last_volume if info and hasattr(info, 'last_volume') else standard_info.get('volume')) if 'info' in locals() else None,
            "market_cap": (info.market_cap if info and hasattr(info, 'market_cap') else standard_info.get('marketCap')) if 'info' in locals() else None,
            "pe_ratio": standard_info.get('trailingPE') if 'standard_info' in locals() and standard_info else None
        }

    except Exception as e:
        logger.error(f"Error fetching quote for {ticker}: {str(e)}")
        # In production, custom exceptions should be used
        return {
            "symbol": ticker.upper(),
            "error": "Data Unavailable",
            "details": str(e)
        }

def get_historical_data(ticker: str, period: str = "6mo", interval: str = "1d") -> dict:
    """
    Fetches historical OHLC (Open, High, Low, Close) data for a ticker.
    
    Args:
        ticker (str): The symbol to look up (e.g. NVDA).
        period (str): The data duration (e.g. '1mo', '1y', 'ytd').
        interval (str): The data granularity (e.g. '1d', '1wk').
        
    Returns:
        dict: A dictionary containing the 'symbol' and a list of 'candles'.
    """
    try:
        stock = yf.Ticker(ticker)
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
            "candles": candles
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
