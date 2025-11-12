"""
Anthropic Claude API client implementation.

Provides interface to Claude models for CCE assessment.
"""

from typing import Optional, Dict, Any
import anthropic
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError, APITimeoutError

from .base import (
    BaseAIClient,
    AIResponse,
    AIClientError,
    AIConnectionError as BaseAIConnectionError,
    AIResponseError,
    AIRateLimitError,
    AITimeoutError as BaseAITimeoutError
)


class AnthropicClient(BaseAIClient):
    """
    Anthropic Claude API client.

    Supports Claude 3 family models (Opus, Sonnet, Haiku) for CCE vulnerability assessment.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize Anthropic client.

        Args:
            api_key: Anthropic API key
            model: Model name (e.g., 'claude-3-5-sonnet-20241022', 'claude-3-opus-20240229')
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries
        """
        super().__init__(model, temperature, max_tokens, timeout, max_retries, retry_delay)
        self.client = Anthropic(api_key=api_key, timeout=timeout)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate response using Anthropic API.

        Args:
            prompt: User prompt/message
            system_prompt: Optional system prompt for context
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            AIResponse: Standardized AI response object

        Raises:
            AIClientError: If the request fails
        """
        try:
            response = self._retry_with_backoff(
                self._make_request,
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )

            return self._parse_response(response)

        except APIConnectionError as e:
            raise BaseAIConnectionError(f"Failed to connect to Anthropic API: {str(e)}")
        except RateLimitError as e:
            raise AIRateLimitError(f"Anthropic rate limit exceeded: {str(e)}")
        except APITimeoutError as e:
            raise BaseAITimeoutError(f"Anthropic request timed out: {str(e)}")
        except APIError as e:
            raise AIClientError(f"Anthropic API error: {str(e)}")
        except Exception as e:
            raise AIClientError(f"Unexpected error: {str(e)}")

    def _make_request(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> Any:
        """
        Make actual API request to Anthropic.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Anthropic response object
        """
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        return self.client.messages.create(**kwargs)

    def _parse_response(self, response: Any) -> AIResponse:
        """
        Parse Anthropic response into standardized format.

        Args:
            response: Raw Anthropic response object

        Returns:
            AIResponse: Standardized response object

        Raises:
            AIResponseError: If response format is invalid
        """
        try:
            # Extract content from first content block
            if not response.content or len(response.content) == 0:
                raise AIResponseError("Anthropic response content is empty")

            content = response.content[0].text
            if content is None:
                raise AIResponseError("Anthropic response text is None")

            tokens_used = {
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
                "total": response.usage.input_tokens + response.usage.output_tokens
            }

            return AIResponse(
                content=content,
                raw_response=response,
                model=response.model,
                tokens_used=tokens_used,
                finish_reason=response.stop_reason
            )

        except (AttributeError, IndexError, KeyError) as e:
            raise AIResponseError(f"Failed to parse Anthropic response: {str(e)}")

    def validate_connection(self) -> bool:
        """
        Validate Anthropic API connection.

        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            # Make a minimal test request
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return response is not None
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Claude model.

        Returns:
            Dict containing model information
        """
        info = {
            "provider": "anthropic",
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        # Add known model-specific information
        if "claude-3-opus" in self.model:
            info.update({
                "context_window": 200000,
                "model_family": "claude-3",
                "tier": "opus",
                "description": "Most capable Claude 3 model"
            })
        elif "claude-3-5-sonnet" in self.model or "claude-3-sonnet" in self.model:
            info.update({
                "context_window": 200000,
                "model_family": "claude-3",
                "tier": "sonnet",
                "description": "Balanced performance and speed"
            })
        elif "claude-3-haiku" in self.model:
            info.update({
                "context_window": 200000,
                "model_family": "claude-3",
                "tier": "haiku",
                "description": "Fastest Claude 3 model"
            })

        return info
