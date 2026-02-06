# pyre-ignore[21]: fastapi installed but not found
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import logging

# pyre-ignore[21]: duckduckgo_search installed but not found
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/text")
def search_text(
    query: str = Query(..., description="搜索关键词"),
    max_results: int = Query(10, ge=1, le=50, description="最大结果数量")
) -> Dict[str, Any]:
    """
    DuckDuckGo 文本搜索
    
    执行网页文本搜索，返回相关结果列表。
    
    Args:
        query: 搜索关键词
        max_results: 返回结果数量（1-50）
        
    Returns:
        包含搜索结果的字典
    """
    try:
        logger.info(f"Text search: '{query}' (max_results={max_results})")
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        
        logger.info(f"Found {len(results)} results for '{query}'")
        
        return {
            "query": query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Text search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.get("/news")
def search_news(
    query: str = Query(..., description="搜索关键词"),
    max_results: int = Query(10, ge=1, le=50, description="最大结果数量")
) -> Dict[str, Any]:
    """
    DuckDuckGo 新闻搜索
    
    搜索最新新闻资讯。
    
    Args:
        query: 搜索关键词
        max_results: 返回结果数量（1-50）
        
    Returns:
        包含新闻结果的字典
    """
    try:
        logger.info(f"News search: '{query}' (max_results={max_results})")
        
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=max_results))
        
        logger.info(f"Found {len(results)} news items for '{query}'")
        
        return {
            "query": query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"News search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"新闻搜索失败: {str(e)}")

@router.get("/suggestions")
async def get_suggestions(
    query: str = Query(..., description="搜索关键词（部分）"),
    provider: str = Query("duckduckgo", description="搜索提供商: duckduckgo 或 yahoo")
) -> Dict[str, Any]:
    """
    搜索建议（联想）端点
    
    支持多个搜索提供商：
    - duckduckgo: 通用搜索建议（返回搜索词，需要二次查询）
    - yahoo: Yahoo Finance 金融搜索（返回标准 ticker，可直接使用）
    
    Args:
        query: 部分搜索关键词
        provider: 搜索提供商（默认: duckduckgo）
        
    Returns:
        包含建议列表的字典
    """
    try:
        logger.info(f"Getting suggestions for: '{query}' using provider: {provider}")
        
        # Import search providers service
        # pyre-ignore[21]: app.services not found
        from app.services.search_providers import get_suggestions, SearchProvider
        
        # Validate and normalize provider
        if provider.lower() == "yahoo":
            selected_provider = SearchProvider.YAHOO_FINANCE
        else:
            selected_provider = SearchProvider.DUCKDUCKGO
        
        # Get suggestions from selected provider
        suggestions = await get_suggestions(query, selected_provider)
        
        logger.info(f"Found {len(suggestions)} suggestions from {provider}")
        
        return {
            "query": query,
            "provider": provider,
            "count": len(suggestions),
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Suggestions failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取建议失败: {str(e)}")

@router.get("/images")
def search_images(
    query: str = Query(..., description="搜索关键词"),
    max_results: int = Query(20, ge=1, le=100, description="最大结果数量")
) -> Dict[str, Any]:
    """
    DuckDuckGo 图片搜索
    
    搜索相关图片。
    
    Args:
        query: 搜索关键词
        max_results: 返回结果数量（1-100）
        
    Returns:
        包含图片结果的字典
    """
    try:
        logger.info(f"Image search: '{query}' (max_results={max_results})")
        
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=max_results))
        
        logger.info(f"Found {len(results)} images for '{query}'")
        
        return {
            "query": query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Image search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"图片搜索失败: {str(e)}")
