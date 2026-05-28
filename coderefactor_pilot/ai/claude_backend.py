"""
Claude (Anthropic) AI backend.

Provides integration with Anthropic's Claude models for generating
refactoring suggestions.
"""

from typing import Any, Dict

from coderefactor_pilot.ai.base import BaseAIBackend, AIBackendError


class ClaudeBackend(BaseAIBackend):
    """Anthropic Claude backend for refactoring suggestions.

    Uses the Anthropic Messages API to generate suggestions.
    Supports Claude 3.5 Sonnet, Claude 3 Opus, and other Claude models.

    Attributes:
        name: Backend identifier.
        base_url: Default API endpoint URL.
    """

    name = "Claude"
    base_url = "https://api.anthropic.com/v1/messages"

    # Anthropic API version
    API_VERSION = "2023-06-01"

    def __init__(self, api_key: str = "", model: str = "claude-3-5-sonnet-20241022",
                 base_url: str = "", max_tokens: int = 2048,
                 temperature: float = 0.3):
        """Initialize the Claude backend.

        Args:
            api_key: Anthropic API key.
            model: Model name (default: claude-3-5-sonnet-20241022).
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
        """Get a refactoring suggestion from Claude.

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
                "Claude API key not configured. Set it with --ai-key or in config.",
                backend_name=self.name,
            )

        prompt = self._build_prompt(issue, code_context)

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
        }

        data = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        response = self._make_request(self.base_url, headers, data)

        try:
            return response["content"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            raise AIBackendError(
                f"Unexpected response format: {str(e)}",
                backend_name=self.name,
            )
