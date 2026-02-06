"""
InvestLens Quant Kernel - Entrypoint
====================================

The main FastAPI application instance serving the Quant Kernel.
This service is responsible for:
1. Handling HTTP REST requests from the frontend.
2. Managing WebSocket connections for real-time data.
3. Orchestrating the "Multi-Model Consensus Engine" workflow.
4. Interfacing with Python quantitative libraries (Pandas, NumPy, TA-Lib).
"""

import logging
# pyre-ignore[21]: fastapi installed but not found
from fastapi import FastAPI, HTTPException, Header
# pyre-ignore[21]: fastapi installed but not found
from fastapi.middleware.cors import CORSMiddleware
# pyre-ignore[21]: app.services not found
from app.services import market_data, consensus
# pyre-ignore[21]: app.routers not found
from app.routers import config, privacy
# pyre-ignore[21]: app.models not found
from app.models.analysis import AnalysisRequest, AnalysisResponse

logger = logging.getLogger(__name__)

# Initialize the FastAPI application with metadata
app = FastAPI(title="InvestLens Quant Kernel", version="0.1.0")

# Configure CORS
# In production, allow_origins should be restricted to the frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """
    Root Endpoint
    -------------
    Provides a basic heartbeat and system identification.
    
    Returns:
        dict: System status and name.
    """
    return {"status": "online", "system": "InvestLens Quant Kernel"}

@app.get("/health")
def health_check():
    """
    Health Check Endpoint
    ---------------------
    Used by the Frontend `SystemStatus` component and Docker healthchecks
    to verify service availability.
    
    Returns:
        dict: Simple 'ok' status.
    """
    return {"message": "InvestLens Quant Kernel is running!", "version": "0.1.0"}

@app.post("/api/v1/models")
async def get_available_models(request: dict):
    """
    Fetch available models from the specified LLM provider endpoint.
    
    Args:
        request (dict): Contains base_url and optional api_key
        
    Returns:
        list: Available models from the provider
    """
    # pyre-ignore[21]: openai installed but not found
    from openai import OpenAI
    
    try:
        base_url = request.get("base_url", "https://api.openai.com/v1")
        api_key = request.get("api_key", "sk-placeholder")
        
        logger.info(f"Fetching models from: {base_url}")
        
        # Create temporary client
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Fetch models
        models_response = client.models.list()
        models = [{"id": model.id, "name": model.id} for model in models_response.data]
        
        logger.info(f"Found {len(models)} models")
        return {"models": models}
        
    except Exception as e:
        logger.error(f"Failed to fetch models: {str(e)}")
        # Return some default models as fallback
        return {
            "models": [
                {"id": "gpt-4", "name": "GPT-4"},
                {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
                {"id": "deepseek-chat", "name": "DeepSeek Chat"},
            ],
            "error": str(e)
        }

@app.get("/api/v1/search")
def search_assets(q: str, limit: int = 10):
    """
    Asset Search Endpoint
    ---------------------
    Search for assets by ISIN, ticker, or name.
    Supports autocomplete functionality.
    
    Args:
        q: Search query
        limit: Maximum results to return
        
    Returns:
        Search results with matching assets
    """
    # pyre-ignore[21]: app.services not found
    from app.services import asset_search
    return asset_search.search(q, limit)

@app.get("/api/v1/convert/{identifier}")
def convert_identifier(identifier: str):
    """
    Identifier Conversion Endpoint
    -------------------------------
    Converts ISIN to ticker or validates ticker format.
    
    Args:
        identifier: ISIN code or ticker symbol
        
    Returns:
        Conversion result with ticker
    """
    # pyre-ignore[21]: app.services not found
    from app.services import asset_search
    return asset_search.convert_to_ticker(identifier)

@app.get("/api/v1/quote/{ticker}")
def get_market_quote(ticker: str):
    """
    Market Data Endpoint
    --------------------
    Fetches real-time (or delayed) quote for a ticker or ISIN.
    Automatically converts ISIN to ticker if needed.
    
    Returns basic market info (price, change, etc).
    """
    data = market_data.get_quote(ticker)
    if "error" in data:
         # In a real app, we might want to return 404 or 400 based on error type
         # For now, returning the error dict with 200 is acceptable for the prototype
         return data
    return data

@app.get("/api/v1/market/history/{ticker}")
def get_historical_market_data(ticker: str, period: str = "6mo"):
    """
    Historical Data Endpoint
    ------------------------
    Fetches OHLC candles for charts.
    
    Args:
        ticker (str): Asset symbol.
        period (str): Range (1mo, 3mo, 6mo, 1y, ytd, max).
        
    Returns:
        dict: Candle data structure.
    """
    return market_data.get_historical_data(ticker, period=period)

@app.get("/api/v1/market/prediction/{ticker}")
def get_price_prediction(ticker: str, days: int = 7):
    """
    Predictive Analytics Endpoint
    -----------------------------
    Generates Monte Carlo price forecast.
    **Gated Feature**: Client should only call this if Quant Mode is active.
    
    Args:
        ticker (str): Asset symbol.
        days (int): Forecast horizon.
        
    Returns:
        dict: Predicted path and confidence bands.
    """
    return market_data.get_prediction(ticker, days=days)


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze_asset(
    request: AnalysisRequest,
    x_llm_api_key: str | None = Header(default=None),
    x_llm_base_url: str | None = Header(default=None),
    x_llm_model: str | None = Header(default=None)
):
    """
    Consensus Analysis Endpoint
    ---------------------------
    The core AI Trigger.
    1. Receives a ticker and focus areas.
    2. Invokes the `ConsensusEngine`.
    3. Returns synthesis and arguments.
    
    Args:
        request (AnalysisRequest): Ticker and preferences.
        x_llm_api_key (str, optional): The user's BYO-API key from frontend settings.
        x_llm_base_url (str, optional): The user's custom Base URL for the LLM provider.
        x_llm_model (str, optional): The model to use for generation.
        
    Returns:
        AnalysisResponse: The AI report.
    """
    try:
        logger.info(f"Received analysis request for {request.ticker}")
        logger.info(f"API Key provided: {bool(x_llm_api_key)}")
        logger.info(f"Base URL provided: {x_llm_base_url}")
        logger.info(f"Model provided: {x_llm_model}")
        
        response = consensus.generate_consensus_analysis(
            ticker=request.ticker,
            focus_areas=request.focus_areas,
            api_key=x_llm_api_key,
            base_url=x_llm_base_url,
            model=x_llm_model
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(config.router)
app.include_router(privacy.router)

