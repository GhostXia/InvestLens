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
from openai import OpenAI
import logging

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

    def generate_analysis(self, system_prompt: str, user_prompt: str, api_key_override: str = None) -> str:
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
            
        Returns:
            str: The raw generated text content from the model's response.
        """
        try:
            logger.info(f"Calling LLM: {self.model} at {self.base_url}")
            
            # Determine which client/key to use
            client = self.client
            if api_key_override:
                # If a user key is provided, we instantiate a temporary client
                # This is lightweight enough for the prototype
                from openai import OpenAI
                client = OpenAI(
                    api_key=api_key_override,
                    base_url=self.base_url
                )
            
            # Basic Chat Completion call
            # We use a relatively high max_tokens to ensure full reports are not truncated
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7, # Balanced creativity and precision
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM Generation Failed: {str(e)}")
            # Fallback for when API is not configured or fails
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
