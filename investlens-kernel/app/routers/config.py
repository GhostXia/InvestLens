# pyre-ignore[21]: fastapi installed but not found
from fastapi import APIRouter, HTTPException
from typing import List
# pyre-ignore[21]: pydantic installed but not found
from pydantic import BaseModel
# pyre-ignore[21]: relative import issue in IDE
from ..services.config_manager import config_manager, DataSourceConfig
# pyre-ignore[21]: relative import issue in IDE
from ..services import market_data

router = APIRouter(prefix="/config", tags=["Configuration"])

class SaveSourcesRequest(BaseModel):
    sources: List[DataSourceConfig]

@router.get("/sources")
def get_sources():
    """
    Retrieve current list of configured data sources.
    """
    return config_manager.load_data_sources()

@router.post("/sources")
def save_sources(payload: SaveSourcesRequest):
    """
    Update data sources and reload providers.
    """
    try:
        # Convert pydantic models to dicts
        sources_data = [s.model_dump() for s in payload.sources]
        config_manager.save_data_sources(sources_data)
        
        # Hot-reload the market data service
        market_data.reload_providers()
        
        return {"status": "success", "message": "Sources saved and providers reloaded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
