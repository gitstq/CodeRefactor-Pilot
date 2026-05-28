"""
AI backend base module.

Defines the abstract base class for AI backends that provide
refactoring suggestions for detected code issues.
"""

import json
import time
from typing import Any, Dict, List, Optional
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


class AIBackendError(Exception):
    """Exception raised when an AI backend operation fails.

    Attributes:
        message: Description of the error.
        backend_name: Name of the backend that raised the error.
    """

    def __init__(self, message: str, backend_name: str = ""):
        """Initialize the error.

        Args:
            message: Error description.
            backend_name: Name of the AI backend.
        """
        self.backend_name = backend_name
        super().__init__(f"[{backend_name}] {message}" if backend_name else message)


class BaseAIBackend:
    """Abstract base class for AI backends.

    Provides a common interface for different AI providers to generate
    refactoring suggestions for code issues.

    Attributes:
        name: Human-readable name of the backend.
        api_key: API key for authentication.
        model: Model identifier to use.
        base_url: Base URL for API requests.
        max_tokens: Maximum tokens in the response.
        temperature: Sampling temperature for generation.
    """

    name: str = ""
    base_url: str = ""

    def __init__(self, api_key: str = "", model: str = "",
                 base_url: str = "", max_tokens: int = 2048,
                 temperature: float = 0.3):
        """Initialize the AI backend.

        Args:
            api_key: API key for authentication.
            model: Model identifier.
            base_url: Base URL for API requests.
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or self.base_url
        self.max_tokens = max_tokens
        self.temperature = temperature

    def get_suggestion(self, issue: Dict[str, Any], code_context: str) -> str:
        """Get a refactoring suggestion for a code issue.

        Args:
            issue: Dictionary containing issue details (rule_id, message, etc.).
            code_context: The relevant source code context.

        Returns:
            Suggested refactoring as a string.

        Raises:
            AIBackendError: If the API request fails.
        """
        raise NotImplementedError("Subclasses must implement get_suggestion")

    def get_batch_suggestions(self, issues: List[Dict[str, Any]],
                              code_contexts: List[str],
                              delay: float = 1.0) -> List[str]:
        """Get suggestions for multiple issues with rate limiting.

        Args:
            issues: List of issue dictionaries.
            code_contexts: List of corresponding code contexts.
            delay: Delay between API calls in seconds.

        Returns:
            List of suggestion strings.

        Raises:
            AIBackendError: If any API request fails.
        """
        suggestions = []
        for issue, context in zip(issues, code_contexts):
            try:
                suggestion = self.get_suggestion(issue, context)
                suggestions.append(suggestion)
            except AIBackendError as e:
                suggestions.append(f"[AI Error] {str(e)}")

            if delay > 0:
                time.sleep(delay)

        return suggestions

    def _build_prompt(self, issue: Dict[str, Any], code_context: str) -> str:
        """Build the prompt for the AI model.

        Args:
            issue: Issue dictionary.
            code_context: Source code context.

        Returns:
            Formatted prompt string.
        """
        return f"""You are a code review expert. Analyze the following code issue and provide a specific, actionable refactoring suggestion.

Issue: {issue.get('rule_name', 'Unknown')} ({issue.get('rule_id', '')})
Severity: {issue.get('severity', 'medium')}
Message: {issue.get('message', '')}
File: {issue.get('file_path', '')}
Line: {issue.get('line', '')}

Code context:
```
{code_context}
```

Provide a brief explanation and the refactored code. Be specific and practical."""

    def _make_request(self, url: str, headers: Dict[str, str],
                      data: Dict[str, Any]) -> Dict[str, Any]:
        """Make an HTTP POST request to the AI API.

        Args:
            url: API endpoint URL.
            headers: HTTP headers.
            data: Request body data.

        Returns:
            Parsed JSON response.

        Raises:
            AIBackendError: If the request fails.
        """
        try:
            req = Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                pass
            raise AIBackendError(
                f"HTTP {e.code}: {error_body[:200]}",
                backend_name=self.name,
            )
        except URLError as e:
            raise AIBackendError(
                f"Connection error: {str(e.reason)}",
                backend_name=self.name,
            )
        except json.JSONDecodeError as e:
            raise AIBackendError(
                f"Invalid JSON response: {str(e)}",
                backend_name=self.name,
            )
        except Exception as e:
            raise AIBackendError(
                f"Request failed: {str(e)}",
                backend_name=self.name,
            )

    def is_configured(self) -> bool:
        """Check if the backend is properly configured.

        Returns:
            True if the backend has the required configuration.
        """
        return bool(self.api_key)
