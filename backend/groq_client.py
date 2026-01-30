"""
Groq API Client for AI Code Generation
"""
import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional

import anyio
from groq import Groq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqClient:
    """Client for interacting with Groq API"""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        # Limit concurrent Groq requests to avoid hitting rate limits
        max_concurrent = int(os.getenv("GROQ_MAX_CONCURRENT", "3"))
        self._semaphore = asyncio.Semaphore(max_concurrent)

        self.client = Groq(api_key=self.api_key)
        logger.info(
            "GroqClient initialized with model=%s, max_concurrent=%s",
            self.model,
            max_concurrent,
        )

    async def _create_completion(self, messages, temperature: float, max_tokens: int):
        """
        Run the synchronous Groq client in a worker thread so we don't block the event loop.
        """

        def _call():
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stream=False,
            )

        return await anyio.to_thread.run_sync(_call)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000,
    ) -> str:
        """
        Generate text using Groq API.

        - Executes the blocking client in a background thread.
        - Applies a simple concurrency limit using a semaphore.
        - Returns a generic error message to callers to avoid leaking internals.
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            logger.info("Sending request to Groq API with %s chars", len(prompt))
            
            # Retry logic for rate limits
            max_retries = 3
            base_delay = 2
            
            for attempt in range(max_retries):
                try:
                    async with self._semaphore:
                        response = await self._create_completion(
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                    break # Success, exit loop
                    
                except Exception as e:
                    # Check for rate limit (Groq usually behaves like OpenAI, 429)
                    # We'll check the error string or type since we don't have the explicit type imported here easily
                    error_str = str(e).lower()
                    if "rate limit" in error_str or "429" in error_str:
                        if attempt < max_retries - 1:
                            wait_time = base_delay * (2 ** attempt)
                            logger.warning(f"Groq Rate Limit hit. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                            await asyncio.sleep(wait_time)
                            continue
                    
                    # If not rate limit or retries exhausted, re-raise
                    logger.error(f"Groq API error: {e}")
                    raise

            result = response.choices[0].message.content
            logger.info("Received response of %s chars", len(result))
            return result

        except Exception as e:
            logger.error(f"Groq API error after retries: {e}")
            raise

    async def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_format: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response
        """
        if json_format:
            enhanced_prompt = f"""{prompt}

IMPORTANT: Return ONLY valid JSON. No markdown, no code blocks, no additional text.
The JSON should be parseable by json.loads() directly."""
        else:
            enhanced_prompt = prompt

        response = await self.generate(enhanced_prompt, system_prompt)

        if json_format:
            try:
                # Remove any markdown code blocks
                cleaned = response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]

                return json.loads(cleaned.strip())
            except json.JSONDecodeError as e:
                logger.error(
                    "Failed to parse JSON from Groq response: %s\nResponse (truncated): %s",
                    e,
                    response[:200],
                )
                return {"error": "Failed to parse JSON", "raw_response": response[:500]}

        return response


# Global instance
groq_client = GroqClient()