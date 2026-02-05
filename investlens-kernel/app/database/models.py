"""
Database Models
===============

SQLite database models for asset metadata and ISIN-to-Ticker mappings.
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Database file location
DB_PATH = Path(__file__).parent.parent.parent / "data" / "assets.db"

def init_database():
    """
    Initialize the SQLite database with required tables.
    Creates the database file if it doesn't exist.
    """
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create assets table for ISIN-to-Ticker mapping
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isin TEXT UNIQUE NOT NULL,
            ticker TEXT NOT NULL,
            name TEXT,
            asset_type TEXT,
            exchange TEXT,
            currency TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index for fast ISIN lookup
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_isin ON assets(isin)
    """)
    
    # Create index for ticker lookup
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ticker ON assets(ticker)
    """)
    
    # Create index for name search
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_name ON assets(name)
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")

def seed_initial_data():
    """
    Seed database with common Hong Kong funds and ETFs.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Common HK funds and ETFs
    initial_data = [
        # (ISIN, Ticker, Name, Type, Exchange, Currency)
        ('HK0000181112', '2800.HK', 'Tracker Fund of Hong Kong', 'ETF', 'HKEX', 'HKD'),
        ('HK0000296944', '2828.HK', 'Hang Seng China Enterprises Index ETF', 'ETF', 'HKEX', 'HKD'),
        ('HK0000320223', '3033.HK', 'CSOP Hang Seng TECH Index ETF', 'ETF', 'HKEX', 'HKD'),
        ('HK0000447285', '2822.HK', 'CSOP FTSE China A50 ETF', 'ETF', 'HKEX', 'HKD'),
        ('HK0000175542', '2823.HK', 'iShares A50 China Index ETF', 'ETF', 'HKEX', 'HKD'),
        ('HK0000093390', '2801.HK', 'iShares Core Hang Seng Index ETF', 'ETF', 'HKEX', 'HKD'),
        ('HK0000320215', '3024.HK', 'HSBC Hang Seng TECH Index ETF', 'ETF', 'HKEX', 'HKD'),
    ]
    
    for isin, ticker, name, asset_type, exchange, currency in initial_data:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO assets (isin, ticker, name, asset_type, exchange, currency)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (isin, ticker, name, asset_type, exchange, currency))
        except Exception as e:
            logger.error(f"Error inserting {isin}: {e}")
    
    conn.commit()
    rows_added = cursor.rowcount
    conn.close()
    logger.info(f"Seeded {rows_added} initial assets")
    return rows_added

def get_ticker_from_isin(isin: str) -> str | None:
    """
    Look up Yahoo Finance ticker from ISIN code.
    
    Args:
        isin: ISIN code (e.g., 'HK0000181112')
        
    Returns:
        Ticker symbol (e.g., '2800.HK') or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT ticker FROM assets WHERE isin = ?", (isin,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    return None

def search_assets(query: str, limit: int = 10) -> list[dict]:
    """
    Search assets by ISIN, ticker, or name.
    
    Args:
        query: Search term
        limit: Maximum results to return
        
    Returns:
        List of matching assets with full details
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search_pattern = f"%{query}%"
    
    cursor.execute("""
        SELECT isin, ticker, name, asset_type, exchange, currency
        FROM assets
        WHERE isin LIKE ? OR ticker LIKE ? OR name LIKE ?
        LIMIT ?
    """, (search_pattern, search_pattern, search_pattern, limit))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results

# Initialize database on module import
try:
    init_database()
    # Seed data on first run
    if not DB_PATH.exists() or DB_PATH.stat().st_size == 0:
        seed_initial_data()
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
