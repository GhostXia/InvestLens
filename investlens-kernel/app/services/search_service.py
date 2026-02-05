"""
Web Search Service
==================

Provides web search functionality using DuckDuckGo.
Used to gather news, sentiment, and recent developments for assets.
"""

import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web for the given query.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing title, href, and body.
    """
    try:
        logger.info(f"Searching web for: {query}")
        results = []
        
        with DDGS() as ddgs:
            # text() returns an iterator of results
            ddgs_gen = ddgs.text(query, max_results=max_results)
            for r in ddgs_gen:
                results.append({
                    "title": r.get("title"),
                    "link": r.get("href"),
                    "snippet": r.get("body")
                })
                
        logger.info(f"Found {len(results)} web results")
        return results
        
    except Exception as e:
        logger.error(f"Web search failed: {str(e)}")
        # Debugging: write to file
        with open("search_error.log", "w") as f:
            f.write(str(e))
        # Return empty list on failure so the consensus engine can proceed without search data
        return []
