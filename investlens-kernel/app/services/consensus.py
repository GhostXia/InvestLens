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
from . import market_data, search_service, prompts
import logging

logger = logging.getLogger(__name__)
# pyre-ignore[21]: Imports exist
from .llm_provider import llm_client
# pyre-ignore[21]: Imports exist
from ..models.analysis import AnalysisResponse

def generate_consensus_analysis(ticker: str, focus_areas: list[str], api_key: str | None = None, base_url: str | None = None, model: str | None = None, quant_mode: bool = False, model_configs: list | None = None) -> AnalysisResponse:
    """
    Performs a comprehensive analysis of the given ticker by orchestrating data fetch and AI inference.
    
    Workflow:
    1. **Context Gathering**: Fetches real-time price, change, and metadata from `market_data` service.
    2. **Prompt Engineering**: Constructs a robust prompt with strict Markdown output constraints.
    3. **Inference**: Delegates to `llm_provider` to query the underlying model(s) (OpenAI/DeepSeek).
    4. **Parsing**: Validates and structures the raw text output into strongly-typed `AnalysisResponse`.
    
    Args:
        ticker (str): The asset symbol to analyze.
        focus_areas (list[str]): List of theoretical lenses to apply (e.g., 'Macro', 'Technicals').
        api_key (str | None): User-provided API key for this request session.
        base_url (str | None): User-provided Base URL for the LLM provider.
        model (str | None): User-provided model identifier.
        quant_mode (bool): If True, provides explicit buy/sell recommendations.
        model_configs (list | None): List of ModelConfig dicts for multi-model consensus.
        
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
    logger.info(f"Starting Consensus Analysis for {ticker}...")
    
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

    # Determine which model(s) to query
    # If model_configs is provided, query each enabled model
    # Otherwise, fall back to single-model (legacy) behavior
    
    bull_responses = []
    bear_responses = []
    
    if model_configs and len(model_configs) > 0:
        # Multi-model mode: query each provider
        logger.info(f"Multi-model mode: {len(model_configs)} providers")
        
        for config in model_configs:
            config_name = config.get("name", "Unknown")
            config_key = config.get("apiKey", api_key)
            config_url = config.get("baseUrl", base_url)
            config_model = config.get("model", model)
            
            logger.info(f"Querying {config_name} (Bull)...")
            bull_resp = llm_client.generate_analysis(
                prompts.BULL_PERSONA,
                base_user_prompt,
                api_key_override=config_key,
                base_url_override=config_url,
                model_override=config_model
            )
            bull_responses.append(f"**{config_name}** (Bull):\n{bull_resp}")
            
            logger.info(f"Querying {config_name} (Bear)...")
            bear_resp = llm_client.generate_analysis(
                prompts.BEAR_PERSONA,
                base_user_prompt,
                api_key_override=config_key,
                base_url_override=config_url,
                model_override=config_model
            )
            bear_responses.append(f"**{config_name}** (Bear):\n{bear_resp}")
        
        # Combine responses for the Judge
        bull_response = "\n\n---\n\n".join(bull_responses)
        bear_response = "\n\n---\n\n".join(bear_responses)
    else:
        # Single-model mode (legacy)
        logger.info("Single-model mode")
        
        logger.info("Executing Stage 1a: The Bull Persona")
        bull_response = llm_client.generate_analysis(
            prompts.BULL_PERSONA, 
            base_user_prompt, 
            api_key_override=api_key, 
            base_url_override=base_url, 
            model_override=model
        )

        logger.info("Executing Stage 1b: The Bear Persona")
        bear_response = llm_client.generate_analysis(
            prompts.BEAR_PERSONA, 
            base_user_prompt, 
            api_key_override=api_key, 
            base_url_override=base_url, 
            model_override=model
        )

    # ==========================================
    # STAGE 2: The Judge (The Verdict)
    # ==========================================
    logger.info("Executing Stage 2: The Judge (Consensus)")
    
    # Enhanced prompt for Quant Mode
    sentiment_section = """4. **Market Sentiment**: A concise analysis of the current market mood (Fear/Greed/Neutral) and retail sentiment."""
    
    if quant_mode:
        sentiment_section = """4. **High Risk Trading Plan** (CRITICAL: You MUST use this exact format):
   - **Action**: [BUY / HOLD / SELL]
   - **Entry Strategy**: [Specific Price Zone]
   - **Position Sizing**: [Specific Amount, e.g. "5% of portfolio" or "$2,000"] - DO NOT BE VAGUE.
   - **Exit Targets**:
     - **Target Price**: [Price] (Risk/Reward > 1:3)
     - **Stop Loss**: [Price]
   - **Reasoning**: [Brief justification]"""

    judge_prompt = prompts.JUDGE_INSTRUCTION_TEMPLATE.format(
        base_user_prompt=base_user_prompt,
        bull_response=bull_response,
        bear_response=bear_response,
        sentiment_section=sentiment_section
    )

    # 3. Call AI Model (The Judge)
    raw_text = llm_client.generate_analysis(
        prompts.JUDGE_PERSONA, 
        judge_prompt, 
        api_key_override=api_key, 
        base_url_override=base_url, 
        model_override=model
    )

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
