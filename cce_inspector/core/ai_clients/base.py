"""
Abstract base class for AI clients.

Defines the interface that all AI backend implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AIResponse:
    """
    Standardized AI response format.

    Attributes:
        content: The text content of the AI response
        raw_response: The original response object from the AI provider
        model: The model name used for the request
        tokens_used: Token usage information (input + output)
        finish_reason: Reason for completion (e.g., 'stop', 'length', 'error')
    """
    content: str
    raw_response: Any
    model: str
    tokens_used: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "content": self.content,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "finish_reason": self.finish_reason
        }


class BaseAIClient(ABC):
    """
    Abstract base class for AI clients.

    All AI backend implementations (OpenAI, Anthropic, local LLM) must inherit
    from this class and implement its abstract methods.
    """

    def __init__(
        self,
        model: str,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize AI client with common parameters.

        Args:
            model: Model name/identifier
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts on failure
            retry_delay: Delay between retries in seconds
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate AI response for the given prompt.

        Args:
            prompt: User prompt/message
            system_prompt: Optional system prompt for context
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            AIResponse: Standardized AI response object

        Raises:
            AIClientError: If the request fails after all retries
        """
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the AI service is accessible.

        Returns:
            bool: True if connection is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.

        Returns:
            Dict containing model information (name, capabilities, limits, etc.)
        """
        pass

    def _retry_with_backoff(self, func, *args, **kwargs) -> Any:
        """
        Execute function with exponential backoff retry logic.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from successful function execution

        Raises:
            Exception: If all retry attempts fail
        """
        import time
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
                else:
                    raise last_exception


class AIClientError(Exception):
    """Base exception for AI client errors."""
    pass


class AIConnectionError(AIClientError):
    """Raised when connection to AI service fails."""
    pass


class AIResponseError(AIClientError):
    """Raised when AI response is invalid or cannot be parsed."""
    pass


class AIRateLimitError(AIClientError):
    """Raised when API rate limit is exceeded."""
    pass


class AITimeoutError(AIClientError):
    """Raised when API request times out."""
    pass
