"""
OpenAI AI backend.

Provides integration with OpenAI's GPT models for generating
refactoring suggestions.
"""

from typing import Any, Dict

from coderefactor_pilot.ai.base import BaseAIBackend, AIBackendError


class OpenAIBackend(BaseAIBackend):
    """OpenAI GPT backend for refactoring suggestions.

    Uses the OpenAI Chat Completions API to generate suggestions.
    Supports GPT-4, GPT-3.5-turbo, and other OpenAI models.

    Attributes:
        name: Backend identifier.
        base_url: Default API endpoint URL.
    """

    name = "OpenAI"
    base_url = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key: str = "", model: str = "gpt-4",
                 base_url: str = "", max_tokens: int = 2048,
                 temperature: float = 0.3):
        """Initialize the OpenAI backend.

        Args:
            api_key: OpenAI API key.
            model: Model name (default: gpt-4).
            base_url: Optional custom API base URL.
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

    def get_suggestion(self, issue: Dict[str, Any], code_context: str) -> str:
        """Get a refactoring suggestion from OpenAI.

        Args:
            issue: Issue dictionary with details.
            code_context: Source code context.

        Returns:
            Refactoring suggestion string.

        Raises:
            AIBackendError: If the API request fails.
        """
        if not self.is_configured():
            raise AIBackendError(
                "OpenAI API key not configured. Set it with --ai-key or in config.",
                backend_name=self.name,
            )

        prompt = self._build_prompt(issue, code_context)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
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
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        response = self._make_request(self.base_url, headers, data)

        try:
            return response["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as e:
            raise AIBackendError(
                f"Unexpected response format: {str(e)}",
                backend_name=self.name,
            )
