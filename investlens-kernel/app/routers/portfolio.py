from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging

# pyre-ignore[21]: relative import
from ..services import portfolio_advisor
from ..services.config_manager import config_manager

router = APIRouter(
    prefix="/analysis/portfolio",
    tags=["portfolio"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

class PortfolioAnalysisRequest(BaseModel):
    symbols: List[str]
    model_config_id: Optional[str] = None  # Optional: specific model to use

class PortfolioAnalysisResponse(BaseModel):
    report: str

@router.post("/", response_model=PortfolioAnalysisResponse)
async def analyze_portfolio_endpoint(request: PortfolioAnalysisRequest):
    """
    Generate a high-risk, opinionated portfolio assessment.
    """
    try:
        # Get default model config if not specified
        api_key = None
        base_url = None
        model = None
        
        # Simple config loading (can be enhanced to look up by ID)
        current_config = config_manager.get_current_config()
        if current_config:
             api_key = current_config.get("api_key")
             base_url = current_config.get("base_url")
             model = current_config.get("model")
        
        report = portfolio_advisor.analyze_portfolio(
            symbols=request.symbols,
            api_key=api_key,
            base_url=base_url,
            model=model
        )
        return {"report": report}
    except Exception as e:
        logger.error(f"Portfolio analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
