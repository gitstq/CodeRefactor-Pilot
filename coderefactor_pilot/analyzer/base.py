"""
Analyzer base module.

Defines the abstract base class for all language-specific analyzers.
Analyzers coordinate the application of rules to source code files.
"""

import time
from typing import Any, Dict, List, Optional

from coderefactor_pilot.rules.base import BaseRule, Issue, Severity, AnalysisResult
from coderefactor_pilot.utils.file_utils import read_file


class BaseAnalyzer:
    """Abstract base class for language-specific code analyzers.

    Coordinates the application of rules to source code files and
    collects the results into an AnalysisResult.

    Attributes:
        language: The programming language this analyzer handles.
        rules: List of rules to apply during analysis.
    """

    language: str = ""

    def __init__(self, rules: Optional[List[BaseRule]] = None,
                 config: Optional[Dict[str, Any]] = None):
        """Initialize the analyzer with rules and configuration.

        Args:
            rules: List of rules to apply. If None, uses default rules.
            config: Configuration dictionary for rule thresholds.
        """
        self._rules = rules or []
        self._config = config or {}

    def analyze(self, file_path: str) -> List[Issue]:
        """Analyze a single file and return issues.

        Args:
            file_path: Path to the source file to analyze.

        Returns:
            List of issues found in the file.
        """
        content = read_file(file_path)
        if content is None:
            return []

        issues = []
        for rule in self._rules:
            if rule.is_applicable(self.language):
                try:
                    rule_issues = rule.check(content, file_path, self.language)
                    issues.extend(rule_issues)
                except Exception:
                    # Don't let one failing rule crash the entire analysis
                    pass

        return issues

    def analyze_files(self, file_paths: List[str]) -> AnalysisResult:
        """Analyze multiple files and return a comprehensive result.

        Args:
            file_paths: List of file paths to analyze.

        Returns:
            AnalysisResult containing all issues and statistics.
        """
        start_time = time.time()
        all_issues: List[Issue] = []
        files_with_issues = 0
        lang_stats: Dict[str, Dict[str, int]] = {}

        for file_path in file_paths:
            issues = self.analyze(file_path)
            all_issues.extend(issues)

            if issues:
                files_with_issues += 1

            # Update language stats
            if self.language not in lang_stats:
                lang_stats[self.language] = {
                    "files": 0,
                    "issues": 0,
                }
            lang_stats[self.language]["files"] += 1
            lang_stats[self.language]["issues"] += len(issues)

        elapsed = time.time() - start_time

        return AnalysisResult(
            issues=all_issues,
            files_scanned=len(file_paths),
            files_with_issues=files_with_issues,
            scan_time=elapsed,
            language_stats=lang_stats,
        )

    def add_rule(self, rule: BaseRule) -> None:
        """Add a rule to the analyzer.

        Args:
            rule: Rule to add.
        """
        self._rules.append(rule)

    def remove_rule(self, rule_id: str) -> None:
        """Remove a rule by its ID.

        Args:
            rule_id: ID of the rule to remove.
        """
        self._rules = [r for r in self._rules if r.id != rule_id]

    def get_rules(self) -> List[BaseRule]:
        """Get the list of configured rules.

        Returns:
            List of rules.
        """
        return list(self._rules)

    def get_rule(self, rule_id: str) -> Optional[BaseRule]:
        """Get a rule by its ID.

        Args:
            rule_id: ID of the rule to find.

        Returns:
            The rule if found, None otherwise.
        """
        for rule in self._rules:
            if rule.id == rule_id:
                return rule
        return None

    def list_rules(self) -> List[Dict[str, str]]:
        """List all configured rules with their metadata.

        Returns:
            List of dictionaries with rule information.
        """
        return [
            {
                "id": rule.id,
                "name": rule.name,
                "description": rule.description,
                "severity": rule.severity.value,
                "category": rule.category,
                "languages": ", ".join(rule.languages) if rule.languages else "all",
            }
            for rule in self._rules
        ]
