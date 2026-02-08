"""
LLM Provider Service
====================

A generic adapter for OpenAI-compatible APIs.
Supports connecting to:
- Official OpenAI API
- DeepSeek API
- Ollama (Local)
- Any other conformant endpoint

Configuration is handled via environment variables.
"""

import os
# pyre-ignore[21]: OpenAI is installed but not found by IDE
from openai import OpenAI
import logging
from typing import Optional
# pyre-ignore[21]: tenacity installed but not found
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class LLMProvider:
    """
    Wrapper around the OpenAI Python Client.
    Manages connection and error handling for LLM inference.
    """
    def __init__(self):
        # Load config from env or defaults
        # In a real app, use a proper Config manager (e.g. pydantic-settings)
        self.api_key = os.getenv("LLM_API_KEY", "sk-placeholder")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.timeout = float(os.getenv("LLM_TIMEOUT", "120.0"))

    @retry(
        retry=retry_if_exception_type(Exception), # In prod, be specific: APITimeoutError, etc.
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate_analysis(self, system_prompt: str, user_prompt: str, api_key_override: str | None = None, base_url_override: str | None = None, model_override: str | None = None) -> str:
        """
        Executes a synchronus generation call to the LLM.
        
        This method handles:
        1. Logging of the request context.
        2. Construction of the message payload using the OpenAI Chat format.
        3. Invocation of the API.
        4. Error trapping and fallback routing.
        
        Args:
            system_prompt (str): High-level behavioral instructions (Persona, Format Constraints).
            user_prompt (str): The specific task payload (Ticker, Data Context).
            api_key_override (str, optional): A session-specific key to use instead of the env var.
            base_url_override (str, optional): A session-specific base URL to use instead of the env var.
            model_override (str, optional): A session-specific model to use instead of the env var.
            
        Returns:
            str: The raw generated text content from the model's response.
        """
        try:
            # Determine which base URL and model to use
            base_url = base_url_override if base_url_override else self.base_url
            model = model_override if model_override else self.model
            logger.info(f"Calling LLM: {model} at {base_url}")
            
            # Determine which client/key to use
            client = self.client
            if api_key_override or base_url_override or model_override:
                # If a user key or base URL is provided, we instantiate a temporary client
                # This is lightweight enough for the prototype
                # pyre-ignore[21]: OpenAI is installed
                from openai import OpenAI
                client = OpenAI(
                    api_key=api_key_override if api_key_override else self.api_key,
                    base_url=base_url
                )
            
            # Basic Chat Completion call
            # We use a relatively high max_tokens to ensure full reports are not truncated
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7, # Balanced creativity and precision
                max_tokens=1500,
                timeout=self.timeout # prevent hanging requests (default 120s)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM Generation Failed (Attempt): {str(e)}")
            raise e # Let tenacity retry
            
    def generate_analysis_safe(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Safe wrapper that catches exceptions after retries are exhausted.
        """
        try:
            return self.generate_analysis(system_prompt, user_prompt, **kwargs)
        except Exception:
            return self._mock_fallback(user_prompt)

    def _mock_fallback(self, prompt: str) -> str:
        """
        Provides a mock response when the real API fails or is missing.
        Useful for development without burning tokens.
        """
        logger.warning("Using Mock Fallback Response")
        return (
            "**[MOCK ANALYSIS - LLM Connection Failed]**\n\n"
            "Unable to connect to the configured AI Provider.\n"
            "Please check your `.env` file for `LLM_API_KEY` and `LLM_BASE_URL`.\n\n"
            "### Mock Insight\n"
            "The market is moving sideways. Wait for a breakout."
        )

# Singleton instance
llm_client = LLMProvider()
