"""
Watchlist Router
=================

API endpoints for managing user's watchlist.
"""

# pyre-ignore[21]: fastapi installed but not found
from fastapi import APIRouter, HTTPException
# pyre-ignore[21]: pydantic installed but not found
from pydantic import BaseModel
from typing import Optional, List

# pyre-ignore[21]: relative import issue in IDE
from ..services import watchlist

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


class AddWatchlistRequest(BaseModel):
    symbol: str
    name: Optional[str] = None
    asset_type: Optional[str] = None
    notes: Optional[str] = None


class UpdateWatchlistRequest(BaseModel):
    name: Optional[str] = None
    notes: Optional[str] = None


class ReorderWatchlistRequest(BaseModel):
    symbol_order: List[str]


@router.get("")
def get_watchlist_endpoint():
    """
    Get Watchlist
    -------------
    Returns the user's current watchlist.
    """
    return watchlist.get_watchlist()


@router.post("")
def add_to_watchlist_endpoint(request: AddWatchlistRequest):
    """
    Add to Watchlist
    ----------------
    Adds an asset to the user's watchlist.
    """
    return watchlist.add_to_watchlist(
        symbol=request.symbol,
        name=request.name,
        asset_type=request.asset_type,
        notes=request.notes
    )


@router.delete("/{symbol}")
def remove_from_watchlist_endpoint(symbol: str):
    """
    Remove from Watchlist
    ---------------------
    Removes an asset from the watchlist.
    """
    return watchlist.remove_from_watchlist(symbol)


@router.patch("/{symbol}")
def update_watchlist_item_endpoint(symbol: str, request: UpdateWatchlistRequest):
    """
    Update Watchlist Item
    ---------------------
    Updates an item's metadata (name, notes).
    """
    updates = {}
    if request.name is not None:
        updates["name"] = request.name
    if request.notes is not None:
        updates["notes"] = request.notes
    
    return watchlist.update_watchlist_item(symbol, updates)


@router.post("/reorder")
def reorder_watchlist_endpoint(request: ReorderWatchlistRequest):
    """
    Reorder Watchlist
    -----------------
    Reorders items in the watchlist.
    """
    return watchlist.reorder_watchlist(request.symbol_order)


@router.delete("")
def clear_watchlist_endpoint():
    """
    Clear Watchlist
    ---------------
    Removes all items from the watchlist.
    """
    return watchlist.clear_watchlist()
