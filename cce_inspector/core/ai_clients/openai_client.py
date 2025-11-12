"""
OpenAI API client implementation.

Provides interface to OpenAI GPT models for CCE assessment.
"""

from typing import Optional, Dict, Any
import openai
from openai import OpenAI

from .base import (
    BaseAIClient,
    AIResponse,
    AIClientError,
    AIConnectionError,
    AIResponseError,
    AIRateLimitError,
    AITimeoutError
)


class OpenAIClient(BaseAIClient):
    """
    OpenAI API client for GPT models.

    Supports GPT-4 and GPT-3.5 models for CCE vulnerability assessment.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            model: Model name (e.g., 'gpt-4-turbo-preview', 'gpt-3.5-turbo')
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries
        """
        super().__init__(model, temperature, max_tokens, timeout, max_retries, retry_delay)
        self.client = OpenAI(api_key=api_key, timeout=timeout)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate response using OpenAI API.

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
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self._retry_with_backoff(
                self._make_request,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )

            return self._parse_response(response)

        except openai.APIConnectionError as e:
            raise AIConnectionError(f"Failed to connect to OpenAI API: {str(e)}")
        except openai.RateLimitError as e:
            raise AIRateLimitError(f"OpenAI rate limit exceeded: {str(e)}")
        except openai.APITimeoutError as e:
            raise AITimeoutError(f"OpenAI request timed out: {str(e)}")
        except openai.APIError as e:
            raise AIClientError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise AIClientError(f"Unexpected error: {str(e)}")

    def _make_request(
        self,
        messages: list,
        temperature: float,
        max_tokens: int
    ) -> Any:
        """
        Make actual API request to OpenAI.

        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            OpenAI response object
        """
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def _parse_response(self, response: Any) -> AIResponse:
        """
        Parse OpenAI response into standardized format.

        Args:
            response: Raw OpenAI response object

        Returns:
            AIResponse: Standardized response object

        Raises:
            AIResponseError: If response format is invalid
        """
        try:
            content = response.choices[0].message.content
            if content is None:
                raise AIResponseError("OpenAI response content is None")

            tokens_used = {
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }

            return AIResponse(
                content=content,
                raw_response=response,
                model=response.model,
                tokens_used=tokens_used,
                finish_reason=response.choices[0].finish_reason
            )

        except (AttributeError, IndexError, KeyError) as e:
            raise AIResponseError(f"Failed to parse OpenAI response: {str(e)}")

    def validate_connection(self) -> bool:
        """
        Validate OpenAI API connection.

        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            # Make a minimal test request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return response is not None
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current OpenAI model.

        Returns:
            Dict containing model information
        """
        # OpenAI doesn't provide a direct model info endpoint
        # Return known information based on model name
        info = {
            "provider": "openai",
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        # Add known model-specific information
        if "gpt-4" in self.model.lower():
            info.update({
                "context_window": 128000 if "turbo" in self.model else 8192,
                "training_cutoff": "April 2023"
            })
        elif "gpt-3.5" in self.model.lower():
            info.update({
                "context_window": 16385,
                "training_cutoff": "September 2021"
            })

        return info
