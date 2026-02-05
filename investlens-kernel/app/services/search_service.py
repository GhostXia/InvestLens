"""
Search Service
==============

Provides news gathering capabilities using yfinance (Yahoo Finance).
No API key required - completely free.
"""

import logging
import yfinance as yf

logger = logging.getLogger(__name__)

def search_web(query: str, max_results: int = 5, ticker: str | None = None) -> list[dict]:
    """
    Fetches recent news for a given ticker using yfinance.

    Args:
        query (str): The search query (can be ignored, using ticker instead).
        max_results (int): Maximum number of results to return.
        ticker (str | None): Stock ticker symbol (e.g., 'AAPL', 'NVDA').

    Returns:
        list[dict]: A list of dictionaries containing 'title', 'link', and 'snippet'.
    """
    # Extract ticker from query if not provided
    # Simple heuristic: first word in uppercase
    if not ticker:
        words = query.split()
        ticker = next((w.upper() for w in words if w.isupper()), words[0] if words else "")
    
    if not ticker:
        logger.warning("No ticker provided for news search.")
        return []
    
    results = []
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        
        if not news:
            logger.info(f"No news found for ticker: {ticker}")
            return []
        
        # Format news items
        for item in news[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("publisher", "") + " - " + item.get("title", "")[:150]
            })
    except Exception as e:
        logger.error(f"Failed to fetch news for ticker '{ticker}': {e}")
        # Return empty list on failure so as not to block the main analysis flow
        return []

    return results
