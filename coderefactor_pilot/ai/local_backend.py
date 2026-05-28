"""
Local model (Ollama) AI backend.

Provides integration with locally running Ollama models for generating
refactoring suggestions without requiring an internet connection.
"""

from typing import Any, Dict

from coderefactor_pilot.ai.base import BaseAIBackend, AIBackendError


class LocalBackend(BaseAIBackend):
    """Local Ollama backend for refactoring suggestions.

    Uses the Ollama REST API to generate suggestions with locally
    running models. No API key or internet connection required.

    Attributes:
        name: Backend identifier.
        base_url: Default Ollama API endpoint URL.
    """

    name = "Local (Ollama)"
    base_url = "http://localhost:11434/api/chat"

    def __init__(self, api_key: str = "", model: str = "codellama",
                 base_url: str = "", max_tokens: int = 2048,
                 temperature: float = 0.3):
        """Initialize the Ollama backend.

        Args:
            api_key: Not used for local models, kept for interface consistency.
            model: Model name (default: codellama).
            base_url: Ollama API URL (default: http://localhost:11434/api/chat).
            max_tokens: Maximum response tokens.
            temperature: Sampling temperature.
        """
        super().__init__(
            api_key=api_key,
            model=model,
            base_url=base_url,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def is_configured(self) -> bool:
        """Check if the backend is configured.

        For local Ollama, always returns True since no API key is needed.

        Returns:
            True (local backend is always considered configured).
        """
        return True

    def get_suggestion(self, issue: Dict[str, Any], code_context: str) -> str:
        """Get a refactoring suggestion from a local Ollama model.

        Args:
            issue: Issue dictionary with details.
            code_context: Source code context.

        Returns:
            Refactoring suggestion string.

        Raises:
            AIBackendError: If the Ollama server is not running or request fails.
        """
        prompt = self._build_prompt(issue, code_context)

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a senior code reviewer. Provide concise, actionable refactoring suggestions.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "stream": False,
            "options": {
                "num_predict": self.max_tokens,
                "temperature": self.temperature,
            }
        }

        response = self._make_request(self.base_url, headers, data)

        try:
            return response["message"]["content"].strip()
        except (KeyError, IndexError) as e:
            raise AIBackendError(
                f"Unexpected response format: {str(e)}. "
                f"Make sure Ollama is running and the model '{self.model}' is available.",
                backend_name=self.name,
            )
