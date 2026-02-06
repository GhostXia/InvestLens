"""
Multi-Model Consensus Engine
============================

The core intelligence layer of InvestLens.
Orchestrates the analysis workflow:
1. Gathers context (Market Data).
2. Prompts AI models.
3. Parses and structures the result.

Future State:
- Will spawn parallel tasks for DeepSeek, GPT-4, Claude.
- Will synthesize a final "Meta-Consensus".
Current State:
- Single-pass analysis using the default configured provider.
"""

import json
from datetime import datetime
# pyre-ignore[21]: Imports exist
from . import market_data, search_service
# pyre-ignore[21]: Imports exist
from .llm_provider import llm_client
# pyre-ignore[21]: Imports exist
from ..models.analysis import AnalysisResponse

def generate_consensus_analysis(ticker: str, focus_areas: list[str], api_key: str | None = None, base_url: str | None = None, model: str | None = None, quant_mode: bool = False) -> AnalysisResponse:
    """
    Performs a comprehensive analysis of the given ticker by orchestrating data fetch and AI inference.
    
    Workflow:
    1. **Context Gathering**: Fetches real-time price, change, and metadata from `market_data` service.
    2. **Prompt Engineering**: Constructs a robust prompt with strict Markdown output constraints.
    3. **Inference**: Delegates to `llm_provider` to query the underlying model (OpenAI/DeepSeek).
    4. **Parsing**: Validates and structures the raw text output into strongly-typed `AnalysisResponse`.
    
    Args:
        ticker (str): The asset symbol to analyze.
        focus_areas (list[str]): List of theoretical lenses to apply (e.g., 'Macro', 'Technicals').
        api_key (str | None): User-provided API key for this request session.
        base_url (str | None): User-provided Base URL for the LLM provider.
        model (str | None): User-provided model identifier.
        quant_mode (bool): If True, provides explicit buy/sell recommendations.
        
    Returns:
        AnalysisResponse: A structured object containing the synthesized report and confidence metrics.
    """
    # 1. Fetch live market context
    # If this fails, we let the exception propagate to the API layer (500 Error)
    quote = market_data.get_quote(ticker)
    
    # 1b. Fetch Financials (Best effort)
    financials = market_data.get_financials(ticker)
    fin_context = "\n".join([f"- **{k}**: {v}" for k, v in financials.items()]) if financials else "No recent financial data available."

    # 1c. Fetch Macro Context
    macro = market_data.get_market_context()
    macro_context = ", ".join([f"{k}: {v}" for k, v in macro.items()])
    
    # 1d. Gather Search Context (News/Sentiment)
    search_query = f"{ticker} stock news analysis sentiment"
    search_results = search_service.search_web(search_query, max_results=5)
    
    news_context = "\n".join([
        f"- [{r['title']}]({r['link']}): {r['snippet']}" 
        for r in search_results
    ]) if search_results else "No recent news found via search."

    # ==========================================
    # STAGE 1: Parallel Perspectives (The Debate)
    # ==========================================
    
    # Base Context for all agents
    base_user_prompt = f"""
    Analyze the following asset:
    
    **Asset**: {quote.get('symbol')} ({quote.get('name')})
    **Current Price**: {quote.get('price')} {quote.get('currency')}
    **Change**: {quote.get('change')} ({quote.get('change_percent')}%)
    **Market Context**: {macro_context}
    **Focus Areas**: {', '.join(focus_areas)}
    **Time**: {datetime.now().isoformat()}

    **Financial Snapshot**:
    {fin_context}

    **Recent News & Context**:
    {news_context}
    """

    # --- Perspective A: THE BULL ---
    bull_system = (
        "You are 'The Bull', an optimistic growth investor. "
        "Your goal is to identify maximum upside potential, competitive moats, and growth drivers. "
        "Ignore minor risks unless fatal. Be extremely persuasive about the long case."
    )
    bull_response = llm_client.generate_analysis(bull_system, base_user_prompt, api_key_override=api_key, base_url_override=base_url, model_override=model)

    # --- Perspective B: THE BEAR ---
    bear_system = (
        "You are 'The Bear', a skeptical forensic accountant and risk manager. "
        "Your goal is to identify valuation traps, accounting red flags, and macro headwinds. "
        "Be extremely critical. Assume the company is overhyped."
    )
    bear_response = llm_client.generate_analysis(bear_system, base_user_prompt, api_key_override=api_key, base_url_override=base_url, model_override=model)

    # ==========================================
    # STAGE 2: The Judge (The Verdict)
    # ==========================================
    
    # Enhanced prompt for Quant Mode
    sentiment_section = """4. **Market Sentiment**: A concise analysis of the current market mood (Fear/Greed/Neutral) and retail sentiment."""
    
    if quant_mode:
        sentiment_section = """4. **High Risk Trading Plan**:
   - **Action**: BUY / HOLD / SELL (Specific call based on the winning argument)
   - **Entry Strategy**: Recommended entry price zone.
   - **Position Sizing**: **CRITICAL** - Specify detailed allocation (e.g., "Allocate 5% of portfolio" or "Buy $10,000 worth"). Provide a concrete suggested amount.
   - **Exit Targets**:
     - **Target Price**: Specific price target (3-6 months).
     - **Stop Loss**: Specific stop-loss price.
   - **Reasoning**: Justify with risk/reward ratio."""

    judge_system = (
        "You are InvestLens, an impartial 'LLM-as-a-Judge' Consensus Engine. "
        "Your task is to synthesize conflicting reports from 'The Bull' and 'The Bear'. "
        "weigh the evidence, resolve contradictions, and issue a Final Verdict.\n"
        "Output Format: You must strictly follow the requested structure.\n"
        "Style: Professional, concise, data-driven. Act as the final decision maker."
    )
    
    judge_prompt = f"""
    {base_user_prompt}
    
    ---
    **Perspective A (The Bull Case)**:
    {bull_response}
    
    ---
    **Perspective B (The Bear Case)**:
    {bear_response}
    
    ---
    **YOUR TASK**:
    Synthesize the above perspectives into a final trusted report.
    1. **Executive Summary**: A brief 3-sentence overview of the current setup.
    2. **Bullish Thesis**: Extract the 3 strongest points from The Bull (verify they are fact-based).
    3. **Bearish Thesis**: Extract the 3 strongest risks from The Bear.
    {sentiment_section}
    5. **Confidence Score**: An integer from 0-100. Lower it if Bull and Bear strongly disagree on facts.
    
    Response format:
    ---SUMMARY---
    [Content]
    ---BULL---
    [Content]
    ---BEAR---
    [Content]
    ---SENTIMENT---
    [Content]
    ---SCORE---
    [Integer]
    """

    # 3. Call AI Model (The Judge)
    raw_text = llm_client.generate_analysis(judge_system, judge_prompt, api_key_override=api_key, base_url_override=base_url, model_override=model)

    # 4. Parse the customized format
    # This is a naive parser for the prototype. In prod, use JSON mode.
    try:
        parsed = _parse_custom_format(raw_text, quote, ticker)
    except Exception as e:
        # Fallback if AI output is malformed
        parsed = AnalysisResponse(
            ticker=ticker,
            price_context=quote.get('price', 0.0),
            summary=f"**Analysis Parsing Error**: {str(e)}\n\nRaw Output:\n{raw_text}",
            bullish_case="N/A",
            bearish_case="N/A",
            sentiment_analysis="N/A",
            confidence_score=0
        )

    return parsed

def _parse_custom_format(text: str, quote: dict, ticker: str) -> AnalysisResponse:
    """
    Parses the delimiter-based output from the LLM.
    """
    summary = ""
    bull = ""
    bear = ""
    sentiment = "Market sentiment is neutral/mixed."
    score = 50
    
    # Simple state machine or split
    # Robust approach: Split by tokens
    parts = text.split("---")
    
    for i, part in enumerate(parts):
        token = part.strip()
        if token.startswith("SUMMARY"):
            summary = parts[i+1].strip()
        elif token.startswith("BULL"):
            bull = parts[i+1].strip()
        elif token.startswith("BEAR"):
            bear = parts[i+1].strip()
        elif token.startswith("SENTIMENT"):
            sentiment = parts[i+1].strip()
        elif token.startswith("SCORE"):
            try:
                score_str = parts[i+1].strip()
                # Extract first integer found (handle "85 (High)" cases)
                import re
                match = re.search(r'\d+', score_str)
                if match:
                    score = int(match.group())
            except:
                score = 50

    # Fallback if parsing failed completely (LLM ignored instructions)
    if not summary:
        summary = text # Return raw text as summary

    return AnalysisResponse(
        ticker=ticker.upper(),
        price_context=quote.get('price', 0.0),
        summary=summary,
        bullish_case=bull,
        bearish_case=bear,
        sentiment_analysis=sentiment,
        confidence_score=score
    )
