"""
Search Providers Service
========================

Provides multiple search suggestion providers for autocomplete functionality.
Supports DuckDuckGo (general search), Yahoo Finance (financial data), and AkShare (China market).
"""

from enum import Enum
from typing import List, Dict, Any
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
# pyre-ignore[21]: httpx installed but not found
import httpx

logger = logging.getLogger(__name__)

# Thread pool for running sync akshare functions
_executor = ThreadPoolExecutor(max_workers=2)


class SearchProvider(str, Enum):
    """Available search providers"""
    DUCKDUCKGO = "duckduckgo"
    YAHOO_FINANCE = "yahoo"
    AKSHARE = "akshare"
    CUSTOM = "custom"


async def get_suggestions_custom(query: str) -> List[Dict[str, Any]]:
    """
    Get search suggestions from user-configured custom providers.
    Currently supports Alpha Vantage.
    """
    try:
        logger.info(f"Custom/Configured suggestions for: '{query}'")
        
        # pyre-ignore[21]: app.services not found
        from app.services.config_manager import config_manager
        # pyre-ignore[21]: app.services not found
        from app.services.providers.alpha_vantage import AlphaVantageProvider
        
        sources = config_manager.load_data_sources()
        results = []
        
        for source in sources:
            if not source.get("enabled", True):
                continue
                
            if source["provider_type"] == "alpha_vantage":
                api_key = source.get("api_key")
                if api_key:
                    provider = AlphaVantageProvider(api_key=api_key)
                    # Run sync search in executor to avoid blocking
                    loop = asyncio.get_event_loop()
                    # Wrap the method call in a lambda or simple function for executor
                    # Note: search is synchronous using requests
                    suggestions = await loop.run_in_executor(None, provider.search, query)
                    results.extend(suggestions)
        
        logger.info(f"Custom providers returned {len(results)} suggestions")
        return results[:10] # Limit results
        
    except Exception as e:
        logger.error(f"Custom suggestions failed: {str(e)}")
        return []


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


def _search_akshare_sync(query: str) -> List[Dict[str, Any]]:
    """
    Synchronous AkShare search function (runs in thread pool).
    Searches both A-shares and funds.
    """
    try:
        import akshare as ak
        import pandas as pd
        
        results = []
        query_lower = query.lower()
        
        # Search A-shares by name or code
        try:
            stock_df = ak.stock_info_a_code_name()
            # Filter by code or name containing query
            matches = stock_df[
                stock_df['code'].str.contains(query, case=False, na=False) |
                stock_df['name'].str.contains(query, case=False, na=False)
            ].head(5)
            
            for _, row in matches.iterrows():
                results.append({
                    "ticker": row['code'],
                    "name": row['name'],
                    "exchange": "A股",
                    "asset_type": "Stock",
                    "isAkshare": True
                })
        except Exception as e:
            logger.warning(f"AkShare stock search failed: {e}")
        
        # Search funds by name or code
        try:
            fund_df = ak.fund_name_em()
            # Filter by code or name containing query
            matches = fund_df[
                fund_df['基金代码'].str.contains(query, case=False, na=False) |
                fund_df['基金简称'].str.contains(query, case=False, na=False)
            ].head(5)
            
            for _, row in matches.iterrows():
                results.append({
                    "ticker": row['基金代码'],
                    "name": row['基金简称'],
                    "exchange": "基金",
                    "asset_type": "Fund",
                    "isAkshare": True
                })
        except Exception as e:
            logger.warning(f"AkShare fund search failed: {e}")
        
        return results[:10]  # Limit total results
        
    except ImportError:
        logger.error("AkShare not installed. Run: pip install akshare")
        return []
    except Exception as e:
        logger.error(f"AkShare search failed: {str(e)}")
        return []


async def get_suggestions_akshare(query: str) -> List[Dict[str, Any]]:
    """
    Get search suggestions from AkShare for China market.
    
    Supports searching A-shares and funds by name or code.
    Runs synchronous AkShare functions in a thread pool.
    
    Args:
        query: Search term (Chinese name or stock code)
        
    Returns:
        List of suggestion dictionaries with isAkshare=True flag
    """
    try:
        logger.info(f"AkShare suggestions for: '{query}'")
        
        # Run sync function in thread pool
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(_executor, _search_akshare_sync, query)
        
        logger.info(f"AkShare returned {len(results)} suggestions")
        return results
        
    except Exception as e:
        logger.error(f"AkShare suggestions failed: {str(e)}")
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
    elif provider == SearchProvider.AKSHARE:
        return await get_suggestions_akshare(query)
    elif provider == SearchProvider.CUSTOM:
        return await get_suggestions_custom(query)
    else:
        return await get_suggestions_duckduckgo(query)
