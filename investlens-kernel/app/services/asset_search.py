"""
Asset Search Service
====================

Provides search and autocomplete functionality for assets.
Searches across ISIN codes, tickers, and asset names.
"""

import logging
# pyre-ignore[21]: Import exists
from ..database.models import search_assets, get_ticker_from_isin

logger = logging.getLogger(__name__)

def search(query: str, limit: int = 10) -> dict:
    """
    Search for assets by ISIN, ticker, or name.
    
    Args:
        query: Search term (ISIN, ticker, or name fragment)
        limit: Maximum number of results
        
    Returns:
        Dictionary with search results and metadata
    """
    if not query or len(query) < 2:
        return {
            "query": query,
            "results": [],
            "count": 0
        }
    
    try:
        results = search_assets(query, limit)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Search failed for query '{query}': {e}")
        return {
            "query": query,
            "results": [],
            "count": 0,
            "error": str(e)
        }

def convert_to_ticker(identifier: str) -> dict:
    """
    Convert any identifier (ISIN or ticker) to a valid ticker.
    
    Args:
        identifier: ISIN code or ticker symbol
        
    Returns:
        Dictionary with conversion result
    """
    # Check if it looks like an ISIN (12 chars, starts with 2 letters)
    # pyre-ignore[16]: Pyre has issues with str slicing
    if len(identifier) == 12 and identifier[:2].isalpha():
        ticker = get_ticker_from_isin(identifier)
        if ticker:
            return {
                "input": identifier,
                "type": "isin",
                "ticker": ticker,
                "converted": True
            }
        else:
            return {
                "input": identifier,
                "type": "isin",
                "ticker": None,
                "converted": False,
                "error": "ISIN not found in database"
            }
    else:
        # Assume it's already a ticker
        return {
            "input": identifier,
            "type": "ticker",
            "ticker": identifier,
            "converted": False
        }
