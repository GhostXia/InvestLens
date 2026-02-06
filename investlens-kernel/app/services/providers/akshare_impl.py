"""
AkShare Market Data Provider
============================

Implements BaseDataProvider for China A-shares and funds using AkShare library.
Supports historical data, real-time quotes, and financial metrics.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
# pyre-ignore[21]: relative import
from .base import BaseDataProvider

logger = logging.getLogger(__name__)


def _is_ashare_ticker(ticker: str) -> bool:
    """Check if ticker is an A-share code (6 digits, starts with 0/3/6)."""
    if len(ticker) == 6 and ticker.isdigit():
        return ticker[0] in ('0', '3', '6')
    return False


def _is_fund_code(ticker: str) -> bool:
    """Check if ticker is a fund code (6 digits)."""
    return len(ticker) == 6 and ticker.isdigit()


class AkShareProvider(BaseDataProvider):
    """
    Data provider using AkShare library for China market.
    Supports A-shares, funds, and ETFs.
    """

    def __init__(self):
        self._stock_cache: Optional[Any] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = 60  # Cache for 60 seconds

    def _get_realtime_data(self) -> Any:
        """Get real-time A-share data with caching."""
        import akshare as ak
        
        now = datetime.now()
        if self._stock_cache is not None and self._cache_time is not None:
            if (now - self._cache_time).seconds < self._cache_ttl:
                return self._stock_cache
        
        try:
            self._stock_cache = ak.stock_zh_a_spot_em()
            self._cache_time = now
            return self._stock_cache
        except Exception as e:
            logger.error(f"Failed to fetch real-time data: {e}")
            return None

    def get_quote(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Fetch real-time quote for A-share or fund.
        
        Uses:
        - stock_zh_a_spot_em() for A-shares
        - fund_open_fund_info_em() for funds
        """
        try:
            import akshare as ak
            
            # Try A-share first
            if _is_ashare_ticker(ticker):
                df = self._get_realtime_data()
                if df is None or df.empty:
                    return None
                
                # Find the stock by code
                row = df[df['代码'] == ticker]
                if row.empty:
                    return None
                
                row = row.iloc[0]
                
                price = float(row['最新价']) if row['最新价'] else 0.0
                change = float(row['涨跌额']) if row['涨跌额'] else 0.0
                change_pct = float(row['涨跌幅']) if row['涨跌幅'] else 0.0
                
                return {
                    "symbol": ticker,
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_pct, 2),
                    "name": row['名称'],
                    "currency": "CNY",
                    "volume": int(row['成交量']) if row['成交量'] else 0,
                    "market_cap": float(row['总市值']) if row['总市值'] else 0,
                    "pe_ratio": float(row['市盈率-动态']) if row['市盈率-动态'] else None,
                    "turnover_rate": float(row['换手率']) if row['换手率'] else None,
                    "data_source": "akshare"
                }
            
            # Try fund
            if _is_fund_code(ticker):
                try:
                    fund_info = ak.fund_individual_basic_info_xq(symbol=ticker)
                    if fund_info is not None and not fund_info.empty:
                        # Parse fund info
                        info_dict = {}
                        for _, row in fund_info.iterrows():
                            key = row.iloc[0] if len(row) > 0 else ''
                            val = row.iloc[1] if len(row) > 1 else ''
                            info_dict[key] = val
                        
                        # Get NAV
                        nav_str = info_dict.get('单位净值', '0')
                        nav = float(nav_str) if nav_str and nav_str != '--' else 0.0
                        
                        return {
                            "symbol": ticker,
                            "price": round(nav, 4),
                            "change": 0.0,
                            "change_percent": 0.0,
                            "name": info_dict.get('基金名称', ticker),
                            "currency": "CNY",
                            "fund_type": info_dict.get('基金类型', 'Fund'),
                            "data_source": "akshare"
                        }
                except Exception as e:
                    logger.warning(f"Fund info fetch failed: {e}")
            
            return None
            
        except ImportError:
            logger.error("AkShare not installed. Run: pip install akshare")
            return None
        except Exception as e:
            logger.error(f"AkShare quote failed: {str(e)}")
            return None

    def get_historical(self, ticker: str, period: str = "1y") -> Optional[List[Dict[str, Any]]]:
        """
        Fetch historical OHLCV data for A-share.
        
        Args:
            ticker: Stock code (e.g., "000001")
            period: Time period ("1m", "3m", "6m", "1y", "2y")
            
        Returns:
            List of OHLCV dictionaries with standardized field names
        """
        try:
            import akshare as ak
            
            # Calculate date range
            end_date = datetime.now()
            period_map = {
                "1m": 30,
                "3m": 90,
                "6m": 180,
                "1y": 365,
                "2y": 730
            }
            days = period_map.get(period, 365)
            start_date = end_date - timedelta(days=days)
            
            # Fetch historical data
            df = ak.stock_zh_a_hist(
                symbol=ticker,
                period="daily",
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust="qfq"  # Forward adjusted
            )
            
            if df is None or df.empty:
                return None
            
            # Standardize field names
            result = []
            for _, row in df.iterrows():
                result.append({
                    "date": str(row['日期']),
                    "open": float(row['开盘']),
                    "high": float(row['最高']),
                    "low": float(row['最低']),
                    "close": float(row['收盘']),
                    "volume": int(row['成交量']),
                    "change_percent": float(row['涨跌幅']) if '涨跌幅' in row else 0.0
                })
            
            return result
            
        except Exception as e:
            logger.error(f"AkShare historical failed: {str(e)}")
            return None

    def get_financials(self, ticker: str) -> Dict[str, str]:
        """
        Fetch key financial metrics for A-share.
        """
        try:
            import akshare as ak
            
            # Get financial abstract
            df = ak.stock_financial_abstract_ths(symbol=ticker)
            
            if df is None or df.empty:
                return {}
            
            # Get latest data
            latest = df.iloc[0] if len(df) > 0 else None
            if latest is None:
                return {}
            
            result = {}
            
            # Map common metrics
            metric_map = {
                "营业收入": "Revenue",
                "净利润": "Net Income",
                "毛利率": "Gross Margin",
                "净利率": "Net Margin"
            }
            
            for cn_name, en_name in metric_map.items():
                if cn_name in latest.index:
                    val = latest[cn_name]
                    if val and val != '--':
                        result[en_name] = str(val)
            
            return result
            
        except Exception as e:
            logger.error(f"AkShare financials failed: {str(e)}")
            return {}

    def get_market_context(self) -> Dict[str, str]:
        """
        Fetch China market indices (Shanghai, Shenzhen).
        """
        try:
            import akshare as ak
            
            context = {}
            
            # Get major indices
            try:
                index_df = ak.stock_zh_index_spot_em()
                if index_df is not None and not index_df.empty:
                    # Shanghai Composite
                    sh = index_df[index_df['代码'] == '000001']
                    if not sh.empty:
                        sh_row = sh.iloc[0]
                        context["上证指数"] = f"{sh_row['最新价']:.2f} ({sh_row['涨跌幅']:+.2f}%)"
                    
                    # Shenzhen Component
                    sz = index_df[index_df['代码'] == '399001']
                    if not sz.empty:
                        sz_row = sz.iloc[0]
                        context["深证成指"] = f"{sz_row['最新价']:.2f} ({sz_row['涨跌幅']:+.2f}%)"
            except Exception as e:
                logger.warning(f"Index fetch failed: {e}")
            
            return context
            
        except Exception as e:
            logger.error(f"AkShare market context failed: {str(e)}")
            return {}
