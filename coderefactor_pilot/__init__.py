"""
CodeRefactor Pilot - AI-Powered Code Review & Intelligent Refactoring Suggestion Engine.

A zero-dependency terminal tool for static code smell detection
and AI-driven refactoring suggestions.

Usage:
    python -m coderefactor_pilot scan <path>
    python -m coderefactor_pilot scan --diff
    python -m coderefactor_pilot rules
    python -m coderefactor_pilot version
"""

__version__ = "1.0.0"
__author__ = "CodeRefactor Pilot Team"
__license__ = "MIT"

from coderefactor_pilot.analyzer.base import BaseAnalyzer
from coderefactor_pilot.rules.base import BaseRule, Issue, Severity
from coderefactor_pilot.reporter.base import BaseReporter

__all__ = [
    "BaseAnalyzer",
    "BaseRule",
    "Issue",
    "Severity",
    "BaseReporter",
]
