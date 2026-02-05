"""
Analysis Data Models
====================

Defines the Pydantic models used for the Analysis API.
These ensure strict typing for requests and responses between Frontend and Kernel.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class AnalysisRequest(BaseModel):
    """
    Request payload for the analysis endpoint.
    encapsulates all parameters needed to trigger a consensus run.
    """
    ticker: str = Field(
        ..., 
        description="The standardized asset ticker symbol (e.g., AAPL). Converted to uppercase."
    )
    focus_areas: Optional[List[str]] = Field(
        default=["Technical", "Fundamental", "Sentiment"],
        description=(
            "Specific lenses to focus the analysis on. "
            "Examples: 'Technical Indicators', 'Macro Environment', 'Earnings Growth'."
        )
    )
    model_preference: Optional[str] = Field(
        default="consensus",
        description="Selector for the execution mode: 'consensus' (default), or specific model aliases like 'deepseek'."
    )

class AnalysisResponse(BaseModel):
    """
    Structured response containing the AI analysis.
    """
    ticker: str
    price_context: float = Field(..., description="The price at the time of analysis.")
    summary: str = Field(..., description="High-level executive summary (Markdown).")
    bullish_case: str = Field(..., description="Arguments for the bullish thesis (Markdown).")
    bearish_case: str = Field(..., description="Arguments for the bearish thesis (Markdown).")
    confidence_score: int = Field(..., ge=0, le=100, description="AI confidence score (0-100).")
    # For now, we return a single 'consensus' result. 
    # In the future, this can include individual model outputs.
