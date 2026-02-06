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

def generate_consensus_analysis(ticker: str, focus_areas: list[str], api_key: str | None = None, base_url: str | None = None, model: str | None = None) -> AnalysisResponse:
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
        
    Returns:
        AnalysisResponse: A structured object containing the synthesized report and confidence metrics.
    """
    # 1. Fetch live market context
    # If this fails, we let the exception propagate to the API layer (500 Error)
    quote = market_data.get_quote(ticker)
    
    # 2. Construct the Prompt
    # We use a structured system prompt to force Markdown output
    # The 'Persona' is defined here as an advanced quantitative analyst
    system_prompt = (
        "You are InvestLens, an advanced quantitative AI analyst. "
        "Your goal is to provide a balanced, high-density financial analysis.\n"
        "Output Format: You must strictly follow the requested structure.\n"
        "Style: Professional, concise, data-driven. Avoid hedging language like 'I am an AI'."
    )
    
    # 2b. Gather Search Context (News/Sentiment)
    search_query = f"{ticker} stock news analysis sentiment"
    # Pass ticker to search service if needed for advanced filtering, currently just query
    search_results = search_service.search_web(search_query, max_results=5)
    
    news_context = "\n".join([
        f"- [{r['title']}]({r['link']}): {r['snippet']}" 
        for r in search_results
    ]) if search_results else "No recent news found via search."
    
    # Inject dynamic context into the user prompt
    user_prompt = f"""
    Analyze the following asset:
    
    **Asset**: {quote.get('symbol')} ({quote.get('name')})
    **Current Price**: {quote.get('price')} {quote.get('currency')}
    **Change**: {quote.get('change')} ({quote.get('change_percent')}%)
    **Focus Areas**: {', '.join(focus_areas)}
    **Time**: {datetime.now().isoformat()}

    **Recent News & Context**:
    {news_context}

    Please provide a structured report with the following sections formatted in Markdown:
    
    1. **Executive Summary**: A brief 3-sentence overview of the current setup.
    2. **Bullish Thesis**: 3 key bullet points for the long case.
    3. **Bearish Thesis**: 3 key bullet points for the short/risk case.
    4. **Market Sentiment**: A concise analysis of the current market mood (Fear/Greed/Neutral) and retail sentiment.
    5. **Confidence Score**: An integer from 0-100 indicating conviction in the analysis availability.

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
    
    # 3. Call AI Model
    # Pass the user's specific API key if provided
    raw_text = llm_client.generate_analysis(system_prompt, user_prompt, api_key_override=api_key, base_url_override=base_url, model_override=model)

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
