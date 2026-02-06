
import logging
from datetime import datetime
from typing import List, Dict, Any
import concurrent.futures

from . import market_data
from .llm_provider import llm_client

logger = logging.getLogger(__name__)

# =============================================================================
# PROMPT TEMPLATE (Hedge Fund Manager Persona)
# =============================================================================

PORTFOLIO_ADVISOR_INSTRUCTION = """
You are a ruthless, high-performance Hedge Fund Manager. Your job is to critique the user's portfolio with potential "Alpha" in mind.
You DO NOT care about "diversification" for the sake of safety. You care about MAXIMIZING RETURNS and CUTTING LOSERS.

**Style Guide**:
- **Tone**: Aggressive, direct, opinionated, "Savage".
- **No Hedging**: Do not say "this is not financial advice". Do not be polite.
- **Goal**: Identify weak links and suggest high-conviction moves.

**User Portfolio Context**:
{portfolio_context}

**Market Context**:
{market_context}

**Your Task**:
Produce a markdown report in the following STRICT format:

# ☠️ Portfolio Roast
[One paragraph ruthlessly mocking the portfolio's weaknesses, over-exposure, or mediocrity. Be funny but harsh.]

# 🚨 Critical Vulnerabilities
- [Point 1: e.g., "You are over-exposed to tech, if rates rise you are dead."]
- [Point 2]

# 💎 Hidden Gems (Keepers)
- [Symbol]: [Why it's actually a decent pick, surprisingly]

# ✂️ The Chopping Block (Sell Now)
- [Symbol]: [Why it's trash. Be specific.]

# 🚀 Alpha Moves (Aggressive Optimization)
[Concrete suggestions to reallocate capital. Suggest specific sectors or types of assets to swap into.]

"""

def _fetch_asset_data(symbol: str) -> Dict[str, Any]:
    """Helper to fetch data for a single asset safely."""
    try:
        quote = market_data.get_quote(symbol)
        # Attempt to get some basic history for performance context (1 month return)
        # This is expensive, so maybe skip or do simply
        return {
            "symbol": symbol,
            "data": quote,
            "success": "error" not in quote
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e), "success": False}


def analyze_portfolio(symbols: List[str], api_key: str | None = None, base_url: str | None = None, model: str | None = None) -> str:
    """
    Analyzes a list of symbols using the 'Hedge Fund Manager' persona.
    """
    if not symbols:
        return "Your portfolio is empty. Even cash is a position (a losing one due to inflation). Add some assets."

    # 1. Gather Data (Parallel Fetch)
    logger.info(f"Analyzing portfolio with {len(symbols)} assets: {symbols}")
    
    assets_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_symbol = {executor.submit(_fetch_asset_data, sym): sym for sym in symbols}
        for future in concurrent.futures.as_completed(future_to_symbol):
            assets_data.append(future.result())

    # 2. Build Context
    portfolio_context_lines = []
    for item in assets_data:
        sym = item["symbol"]
        if item["success"]:
            q = item["data"]
            price = q.get("price", "N/A")
            change = q.get("change_percent", "N/A")
            name = q.get("name", sym)
            portfolio_context_lines.append(f"- **{sym}** ({name}): Price {price}, Change {change}%")
        else:
            portfolio_context_lines.append(f"- **{sym}**: Data Unavailable (Error: {item.get('error')})")

    portfolio_context = "\n".join(portfolio_context_lines)

    # 3. Market Context
    macro = market_data.get_market_context()
    market_context = ", ".join([f"{k}: {v}" for k, v in macro.items()])

    # 4. Construct Prompt
    prompt = PORTFOLIO_ADVISOR_INSTRUCTION.format(
        portfolio_context=portfolio_context,
        market_context=market_context
    )

    # 5. Call LLM
    logger.info("Calling LLM for portfolio analysis...")
    response = llm_client.generate_analysis(
        "Hedge Fund Manager",
        prompt,
        api_key_override=api_key,
        base_url_override=base_url,
        model_override=model
    )

    return response
