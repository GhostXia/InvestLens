"""
Holdings Service (Universal)
=============================

Unified holdings/constituents service for all financial products:
- China Funds/ETFs (AkShare)
- US ETFs (yfinance)
- HK ETFs (yfinance)
- Index Constituents (AkShare/yfinance)

Note: All implementation is original, based on official API documentation.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# Asset Type Detection
# =============================================================================

def _detect_asset_type(symbol: str) -> str:
    """
    Intelligently detect asset type from symbol format.
    
    Returns:
        str: One of 'china_fund', 'china_etf', 'us_etf', 'hk_etf', 'index', 'unknown'
    """
    symbol = symbol.strip().upper()
    
    # China fund/ETF: 6 digits
    if len(symbol) == 6 and symbol.isdigit():
        # ETF codes typically start with 5 (SH) or 1 (SZ)
        if symbol.startswith(('5', '1')):
            return 'china_etf'
        # Fund codes: other 6-digit codes
        return 'china_fund'
    
    # Hong Kong: ends with .HK
    if symbol.endswith('.HK'):
        return 'hk_etf'
    
    # China A-share with suffix
    if symbol.endswith(('.SS', '.SZ')):
        return 'china_etf'
    
    # Index detection (common indices)
    index_symbols = {
        # US Indices
        '^GSPC', '^DJI', '^IXIC', '^NDX', '^RUT',
        # China Indices  
        '000300', '000016', '000905', '399006', '399001',
        # HK Indices
        '^HSI', '^HSCE',
    }
    if symbol in index_symbols or symbol.startswith('^'):
        return 'index'
    
    # Default: assume Unknown/Global, let get_holdings try both
    return 'unknown'


# =============================================================================
# China Fund Holdings (AkShare)
# =============================================================================

def _get_latest_report_date() -> str:
    """Get the most recent quarterly report year."""
    now = datetime.now()
    year = now.year
    month = now.month
    
    if month < 3:
        return f"{year - 1}"
    return f"{year}"


def _get_china_fund_holdings(fund_code: str) -> dict:
    """
    Get holdings for China mutual fund using AkShare.
    
    Args:
        fund_code: 6-digit fund code (e.g., "110022")
    """
    # pyre-ignore[21]: akshare installed but not found
    import akshare as ak
    
    try:
        logger.info(f"Fetching China fund holdings: {fund_code}")
        year = _get_latest_report_date()
        
        df = ak.fund_portfolio_hold_em(symbol=fund_code, date=year)
        
        if df is None or df.empty:
            return {"symbol": fund_code, "holdings": [], "error": "No holdings data"}
        
        holdings = []
        for _, row in df.head(10).iterrows():
            holdings.append({
                "code": str(row.get("股票代码", "")),
                "name": str(row.get("股票名称", "")),
                "weight": float(row.get("占净值比例", 0)) if row.get("占净值比例") else 0,
                "shares": float(row.get("持股数", 0)) if row.get("持股数") else 0,
                "market_value": float(row.get("持仓市值", 0)) if row.get("持仓市值") else 0,
            })
        
        report_date = str(df.iloc[0]["季度"]) if "季度" in df.columns else None
        
        return {
            "symbol": fund_code,
            "asset_type": "china_fund",
            "holdings": holdings,
            "report_date": report_date,
            "total_count": len(df)
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch China fund holdings: {e}")
        return {"symbol": fund_code, "holdings": [], "error": str(e)}


# =============================================================================
# US/HK ETF Holdings (yfinance)
# =============================================================================

def _get_yfinance_etf_holdings(symbol: str) -> dict:
    """
    Get ETF holdings using yfinance.
    Works for US ETFs (SPY, QQQ, etc.) and HK ETFs (2800.HK, etc.)
    
    Args:
        symbol: ETF ticker symbol
    """
    # pyre-ignore[21]: yfinance installed but not found
    import yfinance as yf
    
    try:
        logger.info(f"Fetching yfinance ETF holdings: {symbol}")
        ticker = yf.Ticker(symbol)
        
        # Try to get holdings from ticker info
        info = ticker.info or {}
        
        # For ETFs, yfinance may have holdings in 'holdings' field
        raw_holdings = info.get("holdings", [])
        
        holdings = []
        
        if raw_holdings:
            # pyre-ignore[16]: Pyre incorrectly flags list slicing
            holdings_list = list(raw_holdings)[0:10]
            for h in holdings_list:
                holdings.append({
                    "code": h.get("symbol", ""),
                    "name": h.get("holdingName", h.get("symbol", "")),
                    "weight": float(h.get("holdingPercent", 0)) * 100 if h.get("holdingPercent") else 0,
                    "shares": 0,
                    "market_value": 0,
                })
        
        asset_type = "hk_etf" if symbol.endswith(".HK") else "us_etf"
        
        return {
            "symbol": symbol,
            "asset_type": asset_type,
            "name": info.get("longName", info.get("shortName", symbol)),
            "holdings": holdings,
            "total_count": len(holdings),
            "note": "Holdings data may be limited for some ETFs" if not holdings else None
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch yfinance ETF holdings: {e}")
        return {"symbol": symbol, "holdings": [], "error": str(e)}


# =============================================================================
# Index Constituents
# =============================================================================

def _get_index_constituents(symbol: str) -> dict:
    """
    Get index constituent stocks.
    
    Supports:
    - China indices via AkShare (000300 沪深300, etc.)
    - US indices via yfinance
    """
    # pyre-ignore[21]: akshare installed but not found
    import akshare as ak
    
    # China index codes mapping
    china_indices = {
        "000300": "沪深300",
        "000016": "上证50",
        "000905": "中证500",
        "399006": "创业板指",
        "399001": "深证成指",
    }
    
    try:
        clean_symbol = symbol.replace(".", "").upper()
        
        if clean_symbol in china_indices:
            logger.info(f"Fetching China index constituents: {clean_symbol}")
            
            df = ak.index_stock_cons(symbol=clean_symbol)
            
            if df is None or df.empty:
                return {"symbol": symbol, "holdings": [], "error": "No constituents data"}
            
            holdings = []
            for _, row in df.head(20).iterrows():
                holdings.append({
                    "code": str(row.get("品种代码", row.get("股票代码", ""))),
                    "name": str(row.get("品种名称", row.get("股票名称", ""))),
                    "weight": 0,
                    "shares": 0,
                    "market_value": 0,
                })
            
            return {
                "symbol": symbol,
                "asset_type": "index",
                "name": china_indices.get(clean_symbol, symbol),
                "holdings": holdings,
                "total_count": len(df)
            }
        
        # For US indices, try yfinance
        return _get_yfinance_etf_holdings(symbol)
        
    except Exception as e:
        logger.error(f"Failed to fetch index constituents: {e}")
        return {"symbol": symbol, "holdings": [], "error": str(e)}


# =============================================================================
# Unified Public API
# =============================================================================

def get_holdings(symbol: str, asset_type: str = "auto") -> dict:
    """
    Unified holdings API with intelligent routing.
    
    Args:
        symbol: Asset symbol (fund code, ETF ticker, index code)
        asset_type: Force asset type or 'auto' for detection
        
    Returns:
        dict: Holdings data with standardized structure
    """
    if asset_type == "auto":
        asset_type = _detect_asset_type(symbol)
    
    logger.info(f"Getting holdings for {symbol} (type: {asset_type})")
    
    if asset_type == "china_fund":
        return _get_china_fund_holdings(symbol)
    elif asset_type in ("china_etf",):
        return _get_china_fund_holdings(symbol)
    elif asset_type in ("us_etf", "hk_etf"):
        return _get_yfinance_etf_holdings(symbol)
    elif asset_type == "index":
        return _get_index_constituents(symbol)
    elif asset_type == "stock":
        return _get_stock_holders(symbol)
    else:
        # Try ETF first, if empty, try stock holders
        result = _get_yfinance_etf_holdings(symbol)
        if not result.get("holdings"):
            stock_result = _get_stock_holders(symbol)
            if stock_result.get("holdings"):
                return stock_result
        return result

def _get_stock_holders(symbol: str) -> dict:
    """
    Get top institutional holders for a stock.
    """
    import yfinance as yf
    try:
        logger.info(f"Fetching institutional holders for: {symbol}")
        ticker = yf.Ticker(symbol)
        
        # institutional_holders is a DataFrame
        # Columns: Holder, SHARES, Date Reported, % Out, Value
        df = ticker.institutional_holders
        
        if df is None or df.empty:
             return {"symbol": symbol, "holdings": [], "error": "No institutional data"}
             
        holdings = []
        # Take top 10
        for _, row in df.head(10).iterrows():
            # Handle different column names yfinance might use
            holder = row.get("Holder", row.get(0, "Unknown"))
            shares = row.get("Shares", row.get(1, 0))
            value = row.get("Value", row.get(4, 0))
            pct = row.get("% Out", row.get(3, 0))
            
            holdings.append({
                "code": "", # No code for institutions
                "name": str(holder),
                "weight": float(pct) * 100 if pct else 0, # Convert decimal to %
                "shares": int(shares) if shares else 0,
                "market_value": int(value) if value else 0
            })
            
        return {
            "symbol": symbol,
            "asset_type": "stock",
            "name": "Institutional Holders",
            "holdings": holdings,
            "total_count": len(df),
            "report_date": str(df.iloc[0]["Date Reported"]) if "Date Reported" in df.columns else None
        }
    except Exception as e:
        logger.error(f"Failed to fetch stock holders: {e}")
        return {"symbol": symbol, "holdings": [], "error": str(e)}


def get_holdings_with_realtime(symbol: str, asset_type: str = "auto") -> dict:
    """
    Get holdings with real-time price data for each holding.
    
    Args:
        symbol: Asset symbol
        asset_type: Asset type or 'auto'
        
    Returns:
        dict: Holdings enriched with current prices
    """
    # pyre-ignore[21]: relative import
    from .market_data import get_quote
    
    # Get static holdings first
    holdings_data = get_holdings(symbol, asset_type)
    
    if "error" in holdings_data and not holdings_data.get("holdings"):
        return holdings_data
    
    # Enrich with real-time prices
    enriched = []
    for h in holdings_data.get("holdings", []):
        code = h.get("code", "")
        if code:
            try:
                quote = get_quote(code)
                if quote and "error" not in quote:
                    h["price"] = quote.get("price")
                    h["change"] = quote.get("change")
                    h["change_pct"] = quote.get("changePercent")
                else:
                    h["price"] = None
                    h["change"] = None
                    h["change_pct"] = None
            except Exception as e:
                logger.warning(f"Failed to get quote for {code}: {e}")
                h["price"] = None
                h["change"] = None
                h["change_pct"] = None
        enriched.append(h)
    
    holdings_data["holdings"] = enriched
    return holdings_data


# =============================================================================
# Legacy API Compatibility
# =============================================================================

def get_fund_holdings(fund_code: str) -> dict:
    """Legacy API: Get China fund holdings."""
    result = get_holdings(fund_code, "china_fund")
    # Map to legacy format
    if "holdings" in result:
        for h in result["holdings"]:
            h["stock_code"] = h.get("code", "")
            h["stock_name"] = h.get("name", "")
            h["ratio"] = h.get("weight", 0)
    result["fund_code"] = fund_code
    return result
