"""
Local LLM client implementation using Ollama.

Provides interface to locally-hosted LLMs for CCE assessment.
"""

from typing import Optional, Dict, Any
import ollama
from ollama import Client, ResponseError, RequestError

from .base import (
    BaseAIClient,
    AIResponse,
    AIClientError,
    AIConnectionError,
    AIResponseError,
    AITimeoutError
)


class LocalLLMClient(BaseAIClient):
    """
    Local LLM client using Ollama.

    Supports any model available through Ollama (Llama, Mistral, etc.)
    for CCE vulnerability assessment without external API dependencies.
    """

    def __init__(
        self,
        server_url: str = "http://localhost:11434",
        model: str = "llama3.1:latest",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout: int = 120,
        max_retries: int = 3,
        retry_delay: int = 2
    ):
        """
        Initialize Local LLM client.

        Args:
            server_url: Ollama server URL
            model: Model name (e.g., 'llama3.1:latest', 'mistral:latest')
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries
        """
        super().__init__(model, temperature, max_tokens, timeout, max_retries, retry_delay)
        self.server_url = server_url
        self.client = Client(host=server_url)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AIResponse:
        """
        Generate response using local LLM via Ollama.

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

        except RequestError as e:
            raise AIConnectionError(f"Failed to connect to Ollama server at {self.server_url}: {str(e)}")
        except ResponseError as e:
            raise AIResponseError(f"Ollama response error: {str(e)}")
        except TimeoutError as e:
            raise AITimeoutError(f"Ollama request timed out: {str(e)}")
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
        Make actual request to Ollama server.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Ollama response object
        """
        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        options = {
            "temperature": temperature,
            "num_predict": max_tokens  # Ollama uses 'num_predict' for max tokens
        }

        response = self.client.chat(
            model=self.model,
            messages=messages,
            options=options
        )

        return response

    def _parse_response(self, response: Any) -> AIResponse:
        """
        Parse Ollama response into standardized format.

        Args:
            response: Raw Ollama response object

        Returns:
            AIResponse: Standardized response object

        Raises:
            AIResponseError: If response format is invalid
        """
        try:
            # Ollama response structure
            content = response.get("message", {}).get("content")
            if content is None:
                raise AIResponseError("Ollama response content is None")

            # Token usage information
            tokens_used = None
            if "prompt_eval_count" in response or "eval_count" in response:
                tokens_used = {
                    "input": response.get("prompt_eval_count", 0),
                    "output": response.get("eval_count", 0),
                    "total": response.get("prompt_eval_count", 0) + response.get("eval_count", 0)
                }

            # Finish reason
            finish_reason = "stop"
            if response.get("done", False):
                finish_reason = response.get("done_reason", "stop")

            return AIResponse(
                content=content,
                raw_response=response,
                model=response.get("model", self.model),
                tokens_used=tokens_used,
                finish_reason=finish_reason
            )

        except (AttributeError, KeyError) as e:
            raise AIResponseError(f"Failed to parse Ollama response: {str(e)}")

    def validate_connection(self) -> bool:
        """
        Validate Ollama server connection and model availability.

        Returns:
            bool: True if connection is valid and model is available, False otherwise
        """
        try:
            # Check if server is reachable
            models = self.client.list()

            # Check if the specified model is available
            model_names = [m.get("name", "") for m in models.get("models", [])]
            model_available = any(self.model in name for name in model_names)

            if not model_available:
                return False

            # Make a minimal test request
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                options={"num_predict": 5}
            )
            return response is not None

        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current local model.

        Returns:
            Dict containing model information
        """
        info = {
            "provider": "local_llm",
            "server_url": self.server_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        try:
            # Try to get detailed model information from Ollama
            show_response = self.client.show(self.model)
            if show_response:
                info.update({
                    "model_info": show_response.get("modelinfo", {}),
                    "parameters": show_response.get("parameters", ""),
                    "template": show_response.get("template", "")
                })
        except Exception:
            # If show command fails, just return basic info
            pass

        return info

    def list_available_models(self) -> list:
        """
        List all models available on the Ollama server.

        Returns:
            List of available model names

        Raises:
            AIConnectionError: If unable to connect to server
        """
        try:
            response = self.client.list()
            models = response.get("models", [])
            return [model.get("name", "") for model in models]
        except Exception as e:
            raise AIConnectionError(f"Failed to list models from Ollama server: {str(e)}")

    def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama registry.

        Args:
            model_name: Name of the model to pull

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.client.pull(model_name)
            return True
        except Exception:
            return False
