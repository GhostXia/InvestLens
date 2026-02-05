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

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from app.services import market_data, consensus
from app.models.analysis import AnalysisRequest, AnalysisResponse

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
    return {"status": "ok"}

@app.get("/api/v1/quote/{ticker}")
def get_market_quote(ticker: str):
    """
    Market Data Endpoint
    --------------------
    Retrieves the latest quote for the specified ticker.
    Integration point for the 'Asset Analysis Dashboard'.
    
    Args:
        ticker (str): The symbol to look up (e.g. AAPL)
        
    Returns:
        dict: The quote data or an error message.
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
    x_llm_api_key: str | None = Header(default=None)
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
        
    Returns:
        AnalysisResponse: The AI report.
    """
    try:
        response = consensus.generate_consensus_analysis(
            ticker=request.ticker,
            focus_areas=request.focus_areas,
            api_key=x_llm_api_key
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

