"""
Configuration management for CCE Inspector.

This module handles environment variables and application settings using Pydantic.
Supports multiple AI backends: OpenAI, Anthropic Claude, and local LLM (Ollama).
"""

import os
from pathlib import Path
from typing import Literal, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class CCEConfig(BaseSettings):
    """
    Main configuration class for CCE Inspector.

    Loads settings from environment variables or .env file.
    """

    # AI Provider Configuration
    ai_provider: Literal["openai", "anthropic", "local_llm"] = Field(
        default="anthropic",
        description="AI backend to use for analysis"
    )

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    openai_model: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI model to use"
    )
    openai_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for OpenAI responses"
    )
    openai_max_tokens: int = Field(
        default=4096,
        gt=0,
        description="Maximum tokens for OpenAI responses"
    )

    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )
    anthropic_model: str = Field(
        default="claude-3-5-sonnet-20241022",
        description="Anthropic Claude model to use"
    )
    anthropic_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Temperature for Claude responses"
    )
    anthropic_max_tokens: int = Field(
        default=4096,
        gt=0,
        description="Maximum tokens for Claude responses"
    )

    # Local LLM Configuration
    local_llm_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server URL"
    )
    local_llm_model: str = Field(
        default="llama3.1:latest",
        description="Local LLM model name"
    )
    local_llm_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Temperature for local LLM responses"
    )

    # Timeout and Retry Configuration
    api_timeout: int = Field(
        default=120,
        gt=0,
        description="API request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum number of API retry attempts"
    )
    retry_delay: int = Field(
        default=2,
        ge=0,
        description="Delay between retries in seconds"
    )

    # Output Configuration
    output_format: Literal["json", "html", "both"] = Field(
        default="both",
        description="Output format for assessment results"
    )
    output_dir: Path = Field(
        default=Path("./output"),
        description="Directory for output files"
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level"
    )
    log_file: Optional[Path] = Field(
        default=None,
        description="Log file path (None for console only)"
    )

    # Cache Configuration
    enable_cache: bool = Field(
        default=True,
        description="Enable caching of AI responses"
    )
    cache_dir: Path = Field(
        default=Path("./.cache"),
        description="Directory for cache files"
    )
    cache_ttl: int = Field(
        default=86400,
        gt=0,
        description="Cache time-to-live in seconds (default: 24 hours)"
    )

    # Plugin Configuration
    active_plugin: Literal["network", "unix", "windows", "database", "application"] = Field(
        default="network",
        description="Active plugin for asset type"
    )

    @field_validator("openai_api_key", "anthropic_api_key")
    @classmethod
    def validate_api_key(cls, v: Optional[str], info) -> Optional[str]:
        """Validate API key format if provided."""
        if v is not None and len(v.strip()) == 0:
            raise ValueError(f"{info.field_name} cannot be empty string")
        return v

    @field_validator("output_dir", "cache_dir")
    @classmethod
    def validate_directory(cls, v: Path) -> Path:
        """Ensure directory exists."""
        if not v.exists():
            v.mkdir(parents=True, exist_ok=True)
        return v

    def validate_provider_config(self) -> None:
        """
        Validate that required API keys are present for the selected provider.

        Raises:
            ValueError: If required API key is missing for the selected provider.
        """
        if self.ai_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        elif self.ai_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


def load_config() -> CCEConfig:
    """
    Load and validate configuration.

    Returns:
        CCEConfig: Validated configuration object.

    Raises:
        ValueError: If configuration validation fails.
    """
    config = CCEConfig()
    config.validate_provider_config()
    return config


# Global config instance
_config: Optional[CCEConfig] = None


def get_config(reload: bool = False) -> CCEConfig:
    """
    Get the global configuration instance.

    Args:
        reload: If True, reload configuration from environment.

    Returns:
        CCEConfig: Global configuration object.
    """
    global _config
    if _config is None or reload:
        _config = load_config()
    return _config
