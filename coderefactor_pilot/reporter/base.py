"""
Reporter base module.

Defines the abstract base class for report generators and
shared formatting utilities.
"""

from typing import Any, Dict, List

from coderefactor_pilot.rules.base import AnalysisResult, Issue, Severity


# ANSI color codes for terminal output
class Colors:
    """ANSI color escape codes for terminal output.

    Provides color constants for formatted terminal output
    without requiring external dependencies like 'rich'.
    """

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

    @staticmethod
    def disable() -> None:
        """Disable all color codes by setting them to empty strings."""
        for attr in ["RESET", "BOLD", "DIM", "UNDERLINE",
                      "BLACK", "RED", "GREEN", "YELLOW", "BLUE",
                      "MAGENTA", "CYAN", "WHITE",
                      "BG_RED", "BG_GREEN", "BG_YELLOW", "BG_BLUE"]:
            setattr(Colors, attr, "")

    @staticmethod
    def severity_color(severity: Severity) -> str:
        """Get the color code for a severity level.

        Args:
            severity: Severity level.

        Returns:
            ANSI color code string.
        """
        color_map = {
            Severity.LOW: Colors.CYAN,
            Severity.MEDIUM: Colors.YELLOW,
            Severity.HIGH: Colors.RED,
            Severity.CRITICAL: Colors.BOLD + Colors.RED,
        }
        return color_map.get(severity, Colors.WHITE)


class BaseReporter:
    """Abstract base class for report generators.

    Defines the interface for generating reports in different formats.
    Subclasses implement format-specific output generation.

    Attributes:
        name: Human-readable name of the report format.
        extension: Default file extension for this format.
    """

    name: str = ""
    extension: str = ""

    def __init__(self, use_color: bool = True):
        """Initialize the reporter.

        Args:
            use_color: Whether to use color in output (for terminal formats).
        """
        self.use_color = use_color
        if not use_color:
            Colors.disable()

    def generate(self, result: AnalysisResult) -> str:
        """Generate a report from analysis results.

        Args:
            result: Analysis results to report.

        Returns:
            Formatted report string.
        """
        raise NotImplementedError("Subclasses must implement generate method")

    def generate_summary(self, result: AnalysisResult) -> str:
        """Generate a summary section for the report.

        Args:
            result: Analysis results.

        Returns:
            Summary section string.
        """
        lines = []
        lines.append(f"Files scanned: {result.files_scanned}")
        lines.append(f"Files with issues: {result.files_with_issues}")
        lines.append(f"Total issues: {len(result.issues)}")
        lines.append(f"Scan time: {result.scan_time:.3f}s")
        lines.append("")

        # Severity breakdown
        sev_summary = result.severity_summary()
        lines.append("Severity breakdown:")
        for sev in Severity:
            count = sev_summary.get(sev.value, 0)
            color = Colors.severity_color(sev) if self.use_color else ""
            reset = Colors.RESET if self.use_color else ""
            label = sev.value.upper().ljust(10)
            bar = "#" * count
            lines.append(f"  {color}{label}{reset} {count} {bar}")
        lines.append("")

        # Category breakdown
        cat_summary = result.category_summary()
        if cat_summary:
            lines.append("Category breakdown:")
            for category, count in sorted(cat_summary.items(), key=lambda x: -x[1]):
                lines.append(f"  {category.ljust(20)} {count}")
            lines.append("")

        return "\n".join(lines)

    def format_issue(self, issue: Issue) -> str:
        """Format a single issue for display.

        Args:
            issue: Issue to format.

        Returns:
            Formatted issue string.
        """
        color = Colors.severity_color(issue.severity) if self.use_color else ""
        reset = Colors.RESET if self.use_color else ""
        bold = Colors.BOLD if self.use_color else ""

        sev_label = issue.severity.value.upper().ljust(10)
        location = f"{issue.file_path}:{issue.line}"

        parts = [
            f"{color}{bold}[{sev_label}]{reset} {issue.rule_name} ({issue.rule_id}) | {location}",
            f"  {issue.message}",
        ]

        if issue.code_snippet:
            parts.append(f"  {Colors.DIM if self.use_color else ''}{issue.code_snippet}{reset}")

        if issue.suggestion:
            parts.append(f"  {Colors.GREEN if self.use_color else ''}Suggestion: {issue.suggestion}{reset}")

        return "\n".join(parts)
