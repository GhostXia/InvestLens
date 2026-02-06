"""
Watchlist Service
==================

Manages user's watchlist of favorite assets (stocks, funds, ETFs).
Data is persisted locally in a JSON file.
"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Watchlist file path: investlens-kernel/config/watchlist.json
WATCHLIST_FILE = Path(__file__).parent.parent.parent / "config" / "watchlist.json"


def _ensure_config_dir():
    """Ensure config directory exists."""
    WATCHLIST_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_watchlist() -> dict:
    """Load watchlist from JSON file."""
    if not WATCHLIST_FILE.exists():
        return {"items": [], "updated_at": None}
    
    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load watchlist: {e}")
        return {"items": [], "updated_at": None}


def _save_watchlist(data: dict):
    """Save watchlist to JSON file."""
    _ensure_config_dir()
    
    try:
        data["updated_at"] = datetime.now().isoformat()
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Watchlist saved: {len(data.get('items', []))} items")
    except Exception as e:
        logger.error(f"Failed to save watchlist: {e}")
        raise


def get_watchlist() -> dict:
    """
    Get the current watchlist.
    
    Returns:
        dict: Watchlist with items and metadata
    """
    return _load_watchlist()


def add_to_watchlist(
    symbol: str,
    name: Optional[str] = None,
    asset_type: Optional[str] = None,
    notes: Optional[str] = None
) -> dict:
    """
    Add an asset to the watchlist.
    
    Args:
        symbol: Asset symbol (e.g., "AAPL", "110022")
        name: Display name (optional)
        asset_type: Type hint (e.g., "us_stock", "china_fund")
        notes: User notes (optional)
        
    Returns:
        dict: Updated watchlist
    """
    watchlist = _load_watchlist()
    items = watchlist.get("items", [])
    
    # Check if already exists
    symbol_upper = symbol.strip().upper()
    for item in items:
        if item.get("symbol", "").upper() == symbol_upper:
            logger.info(f"{symbol} already in watchlist")
            return watchlist
    
    # Add new item
    new_item = {
        "symbol": symbol.strip(),
        "name": name,
        "asset_type": asset_type,
        "notes": notes,
        "added_at": datetime.now().isoformat()
    }
    
    items.append(new_item)
    watchlist["items"] = items
    
    _save_watchlist(watchlist)
    logger.info(f"Added {symbol} to watchlist")
    
    return watchlist


def remove_from_watchlist(symbol: str) -> dict:
    """
    Remove an asset from the watchlist.
    
    Args:
        symbol: Asset symbol to remove
        
    Returns:
        dict: Updated watchlist
    """
    watchlist = _load_watchlist()
    items = watchlist.get("items", [])
    
    symbol_upper = symbol.strip().upper()
    original_count = len(items)
    
    items = [item for item in items if item.get("symbol", "").upper() != symbol_upper]
    
    if len(items) < original_count:
        watchlist["items"] = items
        _save_watchlist(watchlist)
        logger.info(f"Removed {symbol} from watchlist")
    else:
        logger.info(f"{symbol} not found in watchlist")
    
    return watchlist


def update_watchlist_item(symbol: str, updates: dict) -> dict:
    """
    Update an item in the watchlist.
    
    Args:
        symbol: Asset symbol to update
        updates: Fields to update (name, notes, etc.)
        
    Returns:
        dict: Updated watchlist
    """
    watchlist = _load_watchlist()
    items = watchlist.get("items", [])
    
    symbol_upper = symbol.strip().upper()
    
    for item in items:
        if item.get("symbol", "").upper() == symbol_upper:
            for key, value in updates.items():
                if key not in ("symbol", "added_at"):  # Don't allow changing these
                    item[key] = value
            break
    
    watchlist["items"] = items
    _save_watchlist(watchlist)
    
    return watchlist


def clear_watchlist() -> dict:
    """Clear all items from watchlist."""
    watchlist = {"items": [], "updated_at": datetime.now().isoformat()}
    _save_watchlist(watchlist)
    logger.info("Watchlist cleared")
    return watchlist


def reorder_watchlist(symbol_order: List[str]) -> dict:
    """
    Reorder watchlist items.
    
    Args:
        symbol_order: List of symbols in desired order
        
    Returns:
        dict: Updated watchlist
    """
    watchlist = _load_watchlist()
    items = watchlist.get("items", [])
    
    # Create lookup map
    items_map = {item.get("symbol", "").upper(): item for item in items}
    
    # Reorder based on provided order
    new_items = []
    for symbol in symbol_order:
        symbol_upper = symbol.strip().upper()
        if symbol_upper in items_map:
            new_items.append(items_map.pop(symbol_upper))
    
    # Append any remaining items not in the order list
    new_items.extend(items_map.values())
    
    watchlist["items"] = new_items
    _save_watchlist(watchlist)
    
    return watchlist
