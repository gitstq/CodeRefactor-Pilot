"""
Rules package for CodeRefactor Pilot.

Contains all built-in code analysis rules organized by category.
"""

from coderefactor_pilot.rules.base import BaseRule, Issue, Severity, AnalysisResult

__all__ = [
    "BaseRule",
    "Issue",
    "Severity",
    "AnalysisResult",
]
