"""
AI client implementations for CCE Inspector.

Provides unified interface to multiple AI backends:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3 family)
- Local LLM (via Ollama)
"""

from .base import (
    BaseAIClient,
    AIResponse,
    AIClientError,
    AIConnectionError,
    AIResponseError,
    AIRateLimitError,
    AITimeoutError
)
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .local_llm_client import LocalLLMClient
from .factory import AIClientFactory, create_ai_client

__all__ = [
    "BaseAIClient",
    "AIResponse",
    "AIClientError",
    "AIConnectionError",
    "AIResponseError",
    "AIRateLimitError",
    "AITimeoutError",
    "OpenAIClient",
    "AnthropicClient",
    "LocalLLMClient",
    "AIClientFactory",
    "create_ai_client"
]
