"""
Holdings Router (Universal)
============================

API endpoints for holdings/constituents data across all markets.
Supports China funds/ETFs, US ETFs, HK ETFs, and index constituents.
"""

# pyre-ignore[21]: fastapi installed but not found
from fastapi import APIRouter, HTTPException, Query

# pyre-ignore[21]: relative import issue in IDE
from ..services import fund_holdings

router = APIRouter(prefix="/holdings", tags=["Holdings"])


@router.get("/{symbol}")
def get_holdings_endpoint(
    symbol: str,
    asset_type: str = Query(default="auto", description="Asset type: auto, china_fund, china_etf, us_etf, hk_etf, index")
):
    """
    Get Holdings (Universal)
    ------------------------
    Retrieves holdings/constituents for any supported asset type.
    
    Args:
        symbol: Asset symbol (fund code, ETF ticker, index code)
        asset_type: Force type or 'auto' for intelligent detection
        
    Examples:
        - /holdings/110022 → China fund
        - /holdings/SPY → US ETF  
        - /holdings/2800.HK → HK ETF
        - /holdings/000300 → CSI 300 Index
        
    Returns:
        dict: Holdings with standardized structure
    """
    result = fund_holdings.get_holdings(symbol, asset_type)
    
    if "error" in result and not result.get("holdings"):
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/{symbol}/realtime")
def get_holdings_realtime_endpoint(
    symbol: str,
    asset_type: str = Query(default="auto", description="Asset type: auto, china_fund, china_etf, us_etf, hk_etf, index")
):
    """
    Get Holdings with Real-time Prices
    ------------------------------------
    Retrieves holdings enriched with current prices and changes.
    
    Args:
        symbol: Asset symbol
        asset_type: Asset type or 'auto'
        
    Returns:
        dict: Holdings with real-time price data
    """
    result = fund_holdings.get_holdings_with_realtime(symbol, asset_type)
    
    if "error" in result and not result.get("holdings"):
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


# =============================================================================
# Legacy Fund API (backward compatibility)
# =============================================================================

legacy_router = APIRouter(prefix="/fund", tags=["Fund Holdings (Legacy)"])


@legacy_router.get("/{fund_code}/holdings")
def get_fund_holdings_endpoint(fund_code: str):
    """
    [Legacy] Get Fund Holdings
    --------------------------
    Retrieves the top 10 holdings of a China fund.
    
    Deprecated: Use /holdings/{symbol} instead.
    """
    if not fund_code.isdigit() or len(fund_code) != 6:
        raise HTTPException(
            status_code=400, 
            detail="Invalid fund code. Must be 6 digits."
        )
    
    result = fund_holdings.get_fund_holdings(fund_code)
    
    if "error" in result and not result.get("holdings"):
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@legacy_router.get("/{fund_code}/holdings/realtime")
def get_fund_holdings_realtime_endpoint(fund_code: str):
    """
    [Legacy] Get Fund Holdings with Real-time Prices
    -------------------------------------------------
    
    Deprecated: Use /holdings/{symbol}/realtime instead.
    """
    if not fund_code.isdigit() or len(fund_code) != 6:
        raise HTTPException(
            status_code=400, 
            detail="Invalid fund code. Must be 6 digits."
        )
    
    result = fund_holdings.get_holdings_with_realtime(fund_code, "china_fund")
    
    if "error" in result and not result.get("holdings"):
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result
