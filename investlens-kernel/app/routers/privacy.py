# pyre-ignore[21]: fastapi installed but not found
from fastapi import APIRouter, HTTPException
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/privacy", tags=["Privacy"])

def get_config_dir() -> str:
    """Get the absolute path to the config directory"""
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(current_dir, "config")

def clear_backend_data() -> Dict[str, Any]:
    """
    Clear all backend privacy data files.
    
    Returns:
        Dictionary with cleanup results
    """
    results: Dict[str, Any] = {
        "sources_config_deleted": False,
        "config_dir_existed": False,
        "errors": []
    }
    
    config_dir = get_config_dir()
    
    # Check if config directory exists
    if os.path.exists(config_dir):
        results["config_dir_existed"] = True
        
        # Delete sources.json
        sources_file = os.path.join(config_dir, "sources.json")
        if os.path.exists(sources_file):
            try:
                os.remove(sources_file)
                results["sources_config_deleted"] = True
                logger.info(f"Deleted: {sources_file}")
            except Exception as e:
                error_msg = f"Failed to delete sources.json: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
    else:
        logger.info("Config directory does not exist, nothing to clean")
    
    return results

@router.post("/clear-all")
def clear_all_privacy_data():
    """
    Clear ALL privacy data from backend.
    
    This endpoint will:
    - Delete data source configurations (sources.json)
    - Clear any cached sensitive data
    
    Returns:
        Cleanup status and results
    """
    try:
        results = clear_backend_data()
        
        # Also reload providers to reset state
        try:
            # pyre-ignore[21]: relative import
            from ..services import market_data
            market_data.reload_providers()
            results["providers_reloaded"] = True
        except Exception as e:
            results["errors"].append(f"Provider reload failed: {str(e)}")
        
        return {
            "success": True,
            "message": "Privacy data cleared successfully",
            "details": results
        }
    except Exception as e:
        logger.error(f"Privacy data cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-data-sources")
def clear_data_sources_only():
    """
    Clear only data source configurations.
    
    Returns:
        Cleanup status
    """
    try:
        results = clear_backend_data()
        
        # Reload providers
        try:
            # pyre-ignore[21]: relative import
            from ..services import market_data
            market_data.reload_providers()
            results["providers_reloaded"] = True
        except Exception as e:
            results["errors"].append(f"Provider reload failed: {str(e)}")
        
        return {
            "success": True,
            "message": "Data sources cleared",
            "details": results
        }
    except Exception as e:
        logger.error(f"Data sources cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
def get_privacy_status():
    """
    Get current status of privacy data storage.
    
    Returns:
        Information about what data exists
    """
    config_dir = get_config_dir()
    sources_file = os.path.join(config_dir, "sources.json")
    
    return {
        "config_dir_exists": os.path.exists(config_dir),
        "sources_config_exists": os.path.exists(sources_file),
        "config_dir_path": config_dir
    }
