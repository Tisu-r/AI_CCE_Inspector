"""
AI Client Factory

Provides convenient factory function to instantiate AI clients
based on configuration.
"""

from typing import Optional

from .base import BaseAIClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .local_llm_client import LocalLLMClient
from ..config import CCEConfig


class AIClientFactory:
    """
    Factory for creating AI client instances.
    """

    @staticmethod
    def create_from_config(config: CCEConfig) -> BaseAIClient:
        """
        Create AI client from configuration.

        Args:
            config: CCEConfig instance

        Returns:
            BaseAIClient: Configured AI client instance

        Raises:
            ValueError: If provider is not supported or configuration is invalid
        """
        provider = config.ai_provider.lower()

        if provider == "openai":
            if not config.openai_api_key:
                raise ValueError("OpenAI API key is required but not configured")

            return OpenAIClient(
                api_key=config.openai_api_key,
                model=config.openai_model,
                temperature=config.openai_temperature,
                max_tokens=config.openai_max_tokens,
                timeout=config.api_timeout,
                max_retries=config.max_retries,
                retry_delay=config.retry_delay
            )

        elif provider == "anthropic":
            if not config.anthropic_api_key:
                raise ValueError("Anthropic API key is required but not configured")

            return AnthropicClient(
                api_key=config.anthropic_api_key,
                model=config.anthropic_model,
                temperature=config.anthropic_temperature,
                max_tokens=config.anthropic_max_tokens,
                timeout=config.api_timeout,
                max_retries=config.max_retries,
                retry_delay=config.retry_delay
            )

        elif provider == "local_llm":
            return LocalLLMClient(
                server_url=config.local_llm_url,
                model=config.local_llm_model,
                temperature=config.local_llm_temperature,
                max_tokens=config.anthropic_max_tokens,  # Reuse anthropic max_tokens setting
                timeout=config.api_timeout,
                max_retries=config.max_retries,
                retry_delay=config.retry_delay
            )

        else:
            raise ValueError(
                f"Unsupported AI provider: {provider}. "
                f"Supported providers: openai, anthropic, local_llm"
            )

    @staticmethod
    def create_openai(
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        **kwargs
    ) -> OpenAIClient:
        """
        Create OpenAI client with custom parameters.

        Args:
            api_key: OpenAI API key
            model: Model name
            **kwargs: Additional client parameters

        Returns:
            OpenAIClient: Configured client
        """
        return OpenAIClient(api_key=api_key, model=model, **kwargs)

    @staticmethod
    def create_anthropic(
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        **kwargs
    ) -> AnthropicClient:
        """
        Create Anthropic client with custom parameters.

        Args:
            api_key: Anthropic API key
            model: Model name
            **kwargs: Additional client parameters

        Returns:
            AnthropicClient: Configured client
        """
        return AnthropicClient(api_key=api_key, model=model, **kwargs)

    @staticmethod
    def create_local_llm(
        server_url: str = "http://localhost:11434",
        model: str = "llama3.1:latest",
        **kwargs
    ) -> LocalLLMClient:
        """
        Create Local LLM client with custom parameters.

        Args:
            server_url: Ollama server URL
            model: Model name
            **kwargs: Additional client parameters

        Returns:
            LocalLLMClient: Configured client
        """
        return LocalLLMClient(server_url=server_url, model=model, **kwargs)


def create_ai_client(config: Optional[CCEConfig] = None, **kwargs) -> BaseAIClient:
    """
    Convenience function to create AI client.

    Args:
        config: Optional CCEConfig instance (will load from env if not provided)
        **kwargs: Override parameters for specific provider

    Returns:
        BaseAIClient: Configured AI client

    Examples:
        # Create from environment configuration
        client = create_ai_client()

        # Create with specific config
        config = CCEConfig(ai_provider="anthropic", anthropic_api_key="sk-...")
        client = create_ai_client(config)

        # Create OpenAI client directly
        client = create_ai_client(provider="openai", api_key="sk-...", model="gpt-4")
    """
    # If specific provider params are given, create directly
    if "provider" in kwargs:
        provider = kwargs.pop("provider")
        if provider == "openai":
            return AIClientFactory.create_openai(**kwargs)
        elif provider == "anthropic":
            return AIClientFactory.create_anthropic(**kwargs)
        elif provider == "local_llm":
            return AIClientFactory.create_local_llm(**kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    # Otherwise use config
    if config is None:
        from ..config import get_config
        config = get_config()

    return AIClientFactory.create_from_config(config)
