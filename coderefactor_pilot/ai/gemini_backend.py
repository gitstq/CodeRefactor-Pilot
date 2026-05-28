"""
Gemini (Google) AI backend.

Provides integration with Google's Gemini models for generating
refactoring suggestions.
"""

from typing import Any, Dict

from coderefactor_pilot.ai.base import BaseAIBackend, AIBackendError


class GeminiBackend(BaseAIBackend):
    """Google Gemini backend for refactoring suggestions.

    Uses the Google Generative AI REST API to generate suggestions.
    Supports Gemini Pro, Gemini Ultra, and other Gemini models.

    Attributes:
        name: Backend identifier.
        base_url: Default API endpoint URL template.
    """

    name = "Gemini"
    base_url = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, api_key: str = "", model: str = "gemini-pro",
                 base_url: str = "", max_tokens: int = 2048,
                 temperature: float = 0.3):
        """Initialize the Gemini backend.

        Args:
            api_key: Google AI API key.
            model: Model name (default: gemini-pro).
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

    def _get_api_url(self) -> str:
        """Build the full API URL with model and API key.

        Returns:
            Complete API endpoint URL.
        """
        if self.base_url and "{model}" not in self.base_url:
            # Custom URL provided without template
            url = self.base_url
        else:
            url = self.base_url.format(model=self.model)

        separator = "&" if "?" in url else "?"
        return f"{url}{separator}key={self.api_key}"

    def get_suggestion(self, issue: Dict[str, Any], code_context: str) -> str:
        """Get a refactoring suggestion from Gemini.

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
                "Gemini API key not configured. Set it with --ai-key or in config.",
                backend_name=self.name,
            )

        prompt = self._build_prompt(issue, code_context)

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": self.max_tokens,
                "temperature": self.temperature,
            }
        }

        url = self._get_api_url()
        response = self._make_request(url, headers, data)

        try:
            return response["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            raise AIBackendError(
                f"Unexpected response format: {str(e)}",
                backend_name=self.name,
            )
