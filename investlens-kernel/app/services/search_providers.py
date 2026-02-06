"""
Search Providers Service
========================

Provides multiple search suggestion providers for autocomplete functionality.
Supports DuckDuckGo (general search) and Yahoo Finance (financial data).
"""

from enum import Enum
from typing import List, Dict, Any
import logging
# pyre-ignore[21]: httpx installed but not found
import httpx

logger = logging.getLogger(__name__)


class SearchProvider(str, Enum):
    """Available search providers"""
    DUCKDUCKGO = "duckduckgo"
    YAHOO_FINANCE = "yahoo"


async def get_suggestions_duckduckgo(query: str) -> List[Dict[str, Any]]:
    """
    Get search suggestions from DuckDuckGo autocomplete.
    
    Returns general search suggestions that may need further refinement
    to find actual financial tickers.
    
    Args:
        query: Search term
        
    Returns:
        List of suggestion dictionaries with isDdg=True flag
    """
    try:
        logger.info(f"DuckDuckGo suggestions for: '{query}'")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://ac.duckduckgo.com/ac/",
                params={"q": query},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
        
        suggestions = [{
            "ticker": s.get('phrase', ''),
            "name": f"{s.get('phrase', '')} (Search suggestion)",
            "isDdg": True
        } for s in data if s.get('phrase')]
        
        logger.info(f"DuckDuckGo returned {len(suggestions)} suggestions")
        return suggestions
        
    except Exception as e:
        logger.error(f"DuckDuckGo suggestions failed: {str(e)}")
        return []


async def get_suggestions_yahoo(query: str) -> List[Dict[str, Any]]:
    """
    Get financial search suggestions from Yahoo Finance.
    
    Returns precise financial instrument data with valid tickers
    that can be used directly for analysis.
    
    Args:
        query: Search term
        
    Returns:
        List of suggestion dictionaries with isYahoo=True flag
    """
    try:
        logger.info(f"Yahoo Finance suggestions for: '{query}'")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://query2.finance.yahoo.com/v1/finance/search",
                params={
                    "q": query,
                    "quotesCount": 10,
                    "newsCount": 0,
                    "enableFuzzyQuery": False,
                    "quotesQueryId": "tss_match_phrase_query"
                },
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
        
        quotes = data.get('quotes', [])
        
        suggestions = [{
            "ticker": q.get('symbol'),
            "name": q.get('longname') or q.get('shortname', 'N/A'),
            "exchange": q.get('exchange', ''),
            "asset_type": q.get('quoteType', 'Unknown'),
            "isYahoo": True
        } for q in quotes if q.get('symbol')]
        
        logger.info(f"Yahoo Finance returned {len(suggestions)} suggestions")
        return suggestions
        
    except Exception as e:
        logger.error(f"Yahoo Finance suggestions failed: {str(e)}")
        return []


async def get_suggestions(query: str, provider: SearchProvider = SearchProvider.DUCKDUCKGO) -> List[Dict[str, Any]]:
    """
    Get search suggestions using the specified provider.
    
    Args:
        query: Search term
        provider: Search provider to use (default: DuckDuckGo)
        
    Returns:
        List of suggestion dictionaries
    """
    if provider == SearchProvider.YAHOO_FINANCE:
        return await get_suggestions_yahoo(query)
    else:
        return await get_suggestions_duckduckgo(query)
