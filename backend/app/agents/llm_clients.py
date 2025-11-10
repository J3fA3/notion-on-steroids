"""
LLM client wrappers for Claude and Ollama.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Async client for Claude API (Anthropic).

    Used for high-value, complex reasoning tasks like task inference.
    """

    def __init__(self):
        """Initialize Claude client."""
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not set. Claude client will not work.")

        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = settings.CLAUDE_MAX_TOKENS
        self.temperature = settings.CLAUDE_TEMPERATURE

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text completion using Claude.

        Args:
            system_prompt: System instruction
            user_prompt: User message
            temperature: Sampling temperature (overrides default)
            max_tokens: Max tokens to generate (overrides default)

        Returns:
            Generated text

        Raises:
            Exception: If API call fails after retries
        """
        if not self.client:
            raise ValueError("Claude client not initialized. Check ANTHROPIC_API_KEY.")

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature if temperature is not None else self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            content = response.content[0].text
            logger.info(f"Claude generated {len(content)} characters (model: {self.model})")

            return content

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Generate JSON response using Claude.

        Args:
            system_prompt: System instruction (should specify JSON format)
            user_prompt: User message
            temperature: Sampling temperature

        Returns:
            Parsed JSON dict

        Raises:
            json.JSONDecodeError: If response is not valid JSON
        """
        response_text = await self.generate(system_prompt, user_prompt, temperature)

        # Try to extract JSON from markdown code blocks
        if "```json" in response_text:
            # Extract from code block
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            # Extract from generic code block
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Claude response: {response_text[:200]}")
            raise ValueError(f"Claude did not return valid JSON: {e}")


class OllamaClient:
    """
    Client for Ollama (local LLM).

    Used for bulk, low-stakes operations like message classification.
    """

    def __init__(self):
        """Initialize Ollama client."""
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate text completion using Ollama.

        Args:
            prompt: User prompt
            system_prompt: Optional system instruction
            temperature: Sampling temperature

        Returns:
            Generated text

        Raises:
            Exception: If Ollama is not running or request fails
        """
        try:
            import ollama

            # Note: ollama library doesn't have async support yet, run in executor
            loop = asyncio.get_event_loop()

            def _generate():
                response = ollama.generate(
                    model=self.model,
                    prompt=prompt,
                    system=system_prompt,
                    options={"temperature": temperature},
                )
                return response["response"]

            result = await loop.run_in_executor(None, _generate)
            logger.info(f"Ollama generated {len(result)} characters (model: {self.model})")

            return result

        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise ConnectionError(
                f"Failed to connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: ollama serve"
            )

    async def is_actionable(self, message: str) -> bool:
        """
        Determine if a message contains actionable content.

        Fast classification using local LLM.

        Args:
            message: Message text

        Returns:
            True if message is actionable
        """
        system_prompt = """You are a message classifier. Analyze if the message contains actionable tasks or commitments.

Actionable indicators:
- Action verbs: "send", "review", "schedule", "update", "fix", "create"
- Time constraints: "by tomorrow", "this week", "EOD"
- Requests: "can you", "please", "could you"
- Commitments: "I'll", "I will", "let me"

Non-actionable:
- Greetings: "hi", "thanks", "good morning"
- Acknowledgments: "got it", "ok", "understood"
- Questions without requests: "how are you"

Respond with ONLY "yes" or "no"."""

        prompt = f"Message: {message[:500]}\n\nIs this actionable?"

        try:
            response = await self.generate(prompt, system_prompt, temperature=0.3)
            is_actionable = "yes" in response.lower()[:10]
            logger.info(f"Message classified as {'actionable' if is_actionable else 'not actionable'}")
            return is_actionable
        except Exception as e:
            logger.warning(f"Ollama classification failed, assuming actionable: {e}")
            return True  # Default to actionable if classification fails


# Global instances
_claude_client: Optional[ClaudeClient] = None
_ollama_client: Optional[OllamaClient] = None


def get_claude_client() -> ClaudeClient:
    """Get or create Claude client instance."""
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client


def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client instance."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
