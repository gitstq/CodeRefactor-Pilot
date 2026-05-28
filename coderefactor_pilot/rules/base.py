"""
Rule base module.

Defines the core classes for code analysis rules, issues, and severity levels.
All specific rule implementations should inherit from BaseRule.
"""

import enum
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class Severity(enum.Enum):
    """Severity levels for code issues.

    Attributes:
        LOW: Minor style or preference issues.
        MEDIUM: Code quality issues that should be addressed.
        HIGH: Significant problems that could cause bugs or maintenance issues.
        CRITICAL: Security vulnerabilities or critical bugs.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def from_string(cls, value: str) -> "Severity":
        """Parse a severity level from string.

        Args:
            value: String representation of severity.

        Returns:
            Severity enum value.

        Raises:
            ValueError: If the string does not match any severity level.
        """
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Invalid severity '{value}'. Must be one of: "
                f"{', '.join(s.value for s in cls)}"
            )

    def __ge__(self, other: "Severity") -> bool:
        """Compare severity levels for filtering (>=)."""
        order = {Severity.LOW: 0, Severity.MEDIUM: 1, Severity.HIGH: 2, Severity.CRITICAL: 3}
        return order.get(self, 0) >= order.get(other, 0)

    def __gt__(self, other: "Severity") -> bool:
        """Compare severity levels for filtering (>)."""
        order = {Severity.LOW: 0, Severity.MEDIUM: 1, Severity.HIGH: 2, Severity.CRITICAL: 3}
        return order.get(self, 0) > order.get(other, 0)


@dataclass
class Issue:
    """Represents a single code issue found during analysis.

    Attributes:
        rule_id: Unique identifier for the rule that found this issue.
        rule_name: Human-readable name of the rule.
        severity: Severity level of the issue.
        message: Description of the issue.
        file_path: Path to the file where the issue was found.
        line: Line number where the issue starts (1-indexed).
        end_line: Optional end line number for multi-line issues.
        column: Optional column number.
        code_snippet: The relevant code snippet that triggered the issue.
        suggestion: Optional suggestion for fixing the issue.
        category: Category of the issue (complexity, naming, security, etc.).
        language: Programming language of the file.
    """
    rule_id: str
    rule_name: str
    severity: Severity
    message: str
    file_path: str
    line: int = 1
    end_line: Optional[int] = None
    column: Optional[int] = None
    code_snippet: str = ""
    suggestion: str = ""
    category: str = ""
    language: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to a dictionary for serialization.

        Returns:
            Dictionary representation of the issue.
        """
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "message": self.message,
            "file_path": self.file_path,
            "line": self.line,
            "end_line": self.end_line,
            "column": self.column,
            "code_snippet": self.code_snippet,
            "suggestion": self.suggestion,
            "category": self.category,
            "language": self.language,
        }


class BaseRule:
    """Abstract base class for all code analysis rules.

    Every rule must implement the `check` method and define its metadata
    through class attributes.

    Attributes:
        id: Unique identifier for the rule (e.g., 'CC001').
        name: Human-readable name of the rule.
        description: Detailed description of what the rule checks.
        severity: Default severity level for issues found by this rule.
        category: Category of the rule (complexity, naming, security, etc.).
        languages: List of languages this rule supports.
    """

    id: str = ""
    name: str = ""
    description: str = ""
    severity: Severity = Severity.MEDIUM
    category: str = ""
    languages: List[str] = []

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the rule with optional configuration.

        Args:
            config: Dictionary of configuration options for the rule.
        """
        self._config = config or {}

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Analyze code content and return a list of issues.

        Args:
            content: Source code content to analyze.
            file_path: Path to the source file.
            language: Programming language of the file.

        Returns:
            List of Issue objects found in the code.
        """
        raise NotImplementedError("Subclasses must implement the check method")

    def is_applicable(self, language: str) -> bool:
        """Check if this rule is applicable for the given language.

        Args:
            language: Programming language to check.

        Returns:
            True if the rule supports the given language.
        """
        if not self.languages:
            return True  # Universal rule
        return language.lower() in [l.lower() for l in self.languages]

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value for this rule.

        Args:
            key: Configuration key.
            default: Default value if key is not found.

        Returns:
            Configuration value.
        """
        return self._config.get(key, default)

    def __repr__(self) -> str:
        """String representation of the rule."""
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"


@dataclass
class AnalysisResult:
    """Container for the results of a full code analysis.

    Attributes:
        issues: List of all issues found.
        files_scanned: Number of files scanned.
        files_with_issues: Number of files that had issues.
        scan_time: Time taken for the scan in seconds.
        language_stats: Statistics per language.
    """
    issues: List[Issue] = field(default_factory=list)
    files_scanned: int = 0
    files_with_issues: int = 0
    scan_time: float = 0.0
    language_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def get_issues_by_severity(self, severity: Severity) -> List[Issue]:
        """Filter issues by severity level.

        Args:
            severity: Minimum severity level.

        Returns:
            List of issues at or above the specified severity.
        """
        return [issue for issue in self.issues if issue.severity >= severity]

    def get_issues_by_category(self, category: str) -> List[Issue]:
        """Filter issues by category.

        Args:
            category: Category to filter by.

        Returns:
            List of issues in the specified category.
        """
        return [issue for issue in self.issues if issue.category == category]

    def get_issues_by_file(self, file_path: str) -> List[Issue]:
        """Filter issues by file path.

        Args:
            file_path: File path to filter by.

        Returns:
            List of issues in the specified file.
        """
        return [issue for issue in self.issues if issue.file_path == file_path]

    def severity_summary(self) -> Dict[str, int]:
        """Get count of issues per severity level.

        Returns:
            Dictionary mapping severity level names to counts.
        """
        summary = {s.value: 0 for s in Severity}
        for issue in self.issues:
            summary[issue.severity.value] += 1
        return summary

    def category_summary(self) -> Dict[str, int]:
        """Get count of issues per category.

        Returns:
            Dictionary mapping category names to counts.
        """
        summary: Dict[str, int] = {}
        for issue in self.issues:
            cat = issue.category or "unknown"
            summary[cat] = summary.get(cat, 0) + 1
        return summary

    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis result to a dictionary.

        Returns:
            Dictionary representation of the analysis result.
        """
        return {
            "files_scanned": self.files_scanned,
            "files_with_issues": self.files_with_issues,
            "scan_time": round(self.scan_time, 3),
            "total_issues": len(self.issues),
            "severity_summary": self.severity_summary(),
            "category_summary": self.category_summary(),
            "language_stats": self.language_stats,
            "issues": [issue.to_dict() for issue in self.issues],
        }
