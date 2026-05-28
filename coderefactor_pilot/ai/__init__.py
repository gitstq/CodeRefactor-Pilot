"""
AI backend package for CodeRefactor Pilot.

Provides AI backends for generating refactoring suggestions.
"""

from coderefactor_pilot.ai.base import BaseAIBackend, AIBackendError

__all__ = ["BaseAIBackend", "AIBackendError"]
