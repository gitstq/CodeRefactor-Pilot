"""
TUI Dashboard module.

Provides a simple text-based interactive dashboard for browsing
code review results. Uses only standard library (no curses dependency
for maximum compatibility).
"""

import os
import sys
import time
from typing import List, Optional

from coderefactor_pilot.rules.base import AnalysisResult, Issue, Severity
from coderefactor_pilot.reporter.base import Colors


class Dashboard:
    """Text-based interactive dashboard for browsing analysis results.

    Provides a simple terminal UI for navigating through detected issues,
    filtering by severity and category, and viewing detailed information.

    Attributes:
        result: Analysis results to display.
        current_index: Currently selected issue index.
        filter_severity: Current severity filter.
        filter_category: Current category filter.
    """

    def __init__(self, result: AnalysisResult, use_color: bool = True):
        """Initialize the dashboard.

        Args:
            result: Analysis results to browse.
            use_color: Whether to use colored output.
        """
        self.result = result
        self.use_color = use_color
        if not use_color:
            Colors.disable()

        self.current_index = 0
        self.filter_severity: Optional[Severity] = None
        self.filter_category: Optional[str] = None
        self._running = False

    def get_filtered_issues(self) -> List[Issue]:
        """Get issues matching current filters.

        Returns:
            List of filtered issues.
        """
        issues = self.result.issues

        if self.filter_severity:
            issues = [i for i in issues if i.severity == self.filter_severity]

        if self.filter_category:
            issues = [i for i in issues if i.category == self.filter_category]

        return issues

    def show_progress(self, current: int, total: int, file_path: str = "") -> None:
        """Display a progress indicator during scanning.

        Args:
            current: Current file number.
            total: Total number of files.
            file_path: Path of the file being scanned.
        """
        if total == 0:
            return

        pct = (current / total) * 100
        bar_width = 40
        filled = int(bar_width * current / total)
        bar = "#" * filled + "-" * (bar_width - filled)

        # Clear line and write progress
        sys.stdout.write(f"\r  Scanning: [{bar}] {pct:.0f}% ({current}/{total})")
        if file_path:
            # Truncate long paths
            display_path = file_path if len(file_path) <= 50 else "..." + file_path[-47:]
            sys.stdout.write(f"  {display_path}")
        sys.stdout.flush()

        if current == total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    def show_summary(self) -> None:
        """Display the analysis summary."""
        self._clear_screen()
        self._print_header()

        print(f"\n  Files scanned:     {self.result.files_scanned}")
        print(f"  Files with issues: {self.result.files_with_issues}")
        print(f"  Total issues:      {len(self.result.issues)}")
        print(f"  Scan time:         {self.result.scan_time:.3f}s")
        print()

        # Severity breakdown
        print("  Severity Breakdown:")
        print("  " + "-" * 40)
        sev_summary = self.result.severity_summary()
        max_count = max(sev_summary.values()) if sev_summary else 1

        for sev in Severity:
            count = sev_summary.get(sev.value, 0)
            color = Colors.severity_color(sev)
            reset = Colors.RESET
            label = sev.value.upper().ljust(12)
            bar_len = int(20 * count / max(max_count, 1))
            bar = "#" * bar_len
            print(f"  {color}{label}{reset} {count:>4}  {bar}")

        print()

        # Category breakdown
        cat_summary = self.result.category_summary()
        if cat_summary:
            print("  Category Breakdown:")
            print("  " + "-" * 40)
            for category, count in sorted(cat_summary.items(), key=lambda x: -x[1]):
                label = category.capitalize().ljust(20)
                print(f"  {label} {count}")

        print()

    def show_issues(self) -> None:
        """Display the issues list with navigation."""
        issues = self.get_filtered_issues()

        if not issues:
            print(f"\n  No issues found matching current filters.")
            return

        self.current_index = 0
        self._running = True

        while self._running and self.current_index < len(issues):
            self._clear_screen()
            self._print_header()

            issue = issues[self.current_index]
            self._print_issue_detail(issue, self.current_index + 1, len(issues))

            print()
            self._print_navigation(len(issues))

            try:
                key = self._get_key()
                self._handle_key(key, len(issues))
            except (KeyboardInterrupt, EOFError):
                self._running = False

    def _print_header(self) -> None:
        """Print the dashboard header."""
        bold = Colors.BOLD
        reset = Colors.RESET
        cyan = Colors.CYAN
        print(f"\n  {bold}{cyan}CodeRefactor Pilot - Interactive Dashboard{reset}")
        print(f"  {'=' * 50}")

        if self.filter_severity or self.filter_category:
            filters = []
            if self.filter_severity:
                filters.append(f"severity={self.filter_severity.value}")
            if self.filter_category:
                filters.append(f"category={self.filter_category}")
            print(f"  Filters: {', '.join(filters)}")

    def _print_issue_detail(self, issue: Issue, index: int, total: int) -> None:
        """Print detailed information about a single issue.

        Args:
            issue: Issue to display.
            index: Issue number (1-indexed).
            total: Total number of issues.
        """
        color = Colors.severity_color(issue.severity)
        reset = Colors.RESET
        bold = Colors.BOLD
        green = Colors.GREEN
        dim = Colors.DIM

        print(f"\n  Issue {index} of {total}")
        print(f"  {'-' * 50}")
        print(f"  {bold}Rule:{reset}      {issue.rule_name} ({issue.rule_id})")
        print(f"  {bold}Severity:{reset}  {color}{issue.severity.value.upper()}{reset}")
        print(f"  {bold}Category:{reset}  {issue.category}")
        print(f"  {bold}Location:{reset}  {issue.file_path}:{issue.line}")
        print()
        print(f"  {bold}Message:{reset}")
        print(f"    {issue.message}")

        if issue.code_snippet:
            print()
            print(f"  {bold}Code:{reset}")
            print(f"    {dim}{issue.code_snippet}{reset}")

        if issue.suggestion:
            print()
            print(f"  {green}{bold}Suggestion:{reset}")
            print(f"    {green}{issue.suggestion}{reset}")

    def _print_navigation(self, total: int) -> None:
        """Print navigation instructions.

        Args:
            total: Total number of issues.
        """
        dim = Colors.DIM
        reset = Colors.RESET
        print(f"  {dim}{'-' * 50}{reset}")
        print(f"  {dim}[n] Next  [p] Prev  [q] Quit  [f] Filter  [s] Summary{reset}")

    def _get_key(self) -> str:
        """Wait for and return a single key press.

        Returns:
            The character pressed by the user.
        """
        # Simple input-based approach for maximum compatibility
        try:
            return input("\n  > ").strip().lower()
        except EOFError:
            return "q"

    def _handle_key(self, key: str, total: int) -> None:
        """Handle user key input.

        Args:
            key: Key pressed by the user.
            total: Total number of issues.
        """
        if key in ("q", "quit", "exit"):
            self._running = False
        elif key in ("n", "next"):
            if self.current_index < total - 1:
                self.current_index += 1
        elif key in ("p", "prev", "previous"):
            if self.current_index > 0:
                self.current_index -= 1
        elif key in ("f", "filter"):
            self._show_filter_menu()
        elif key in ("s", "summary"):
            self.show_summary()
            input("\n  Press Enter to continue...")

    def _show_filter_menu(self) -> None:
        """Show the filter configuration menu."""
        print("\n  Filter Options:")
        print("  [0] No filter")
        print("  [1] Low severity")
        print("  [2] Medium severity")
        print("  [3] High severity")
        print("  [4] Critical severity")

        categories = set(i.category for i in self.result.issues)
        if categories:
            cat_list = sorted(categories)
            for i, cat in enumerate(cat_list, start=5):
                print(f"  [{i}] Category: {cat}")

        try:
            choice = input("\n  Select filter: ").strip()
            if choice == "0":
                self.filter_severity = None
                self.filter_category = None
            elif choice == "1":
                self.filter_severity = Severity.LOW
                self.filter_category = None
            elif choice == "2":
                self.filter_severity = Severity.MEDIUM
                self.filter_category = None
            elif choice == "3":
                self.filter_severity = Severity.HIGH
                self.filter_category = None
            elif choice == "4":
                self.filter_severity = Severity.CRITICAL
                self.filter_category = None
            else:
                try:
                    idx = int(choice) - 5
                    if 0 <= idx < len(cat_list):
                        self.filter_category = cat_list[idx]
                        self.filter_severity = None
                except (ValueError, IndexError):
                    pass

            self.current_index = 0
        except (EOFError, KeyboardInterrupt):
            pass

    @staticmethod
    def _clear_screen() -> None:
        """Clear the terminal screen."""
        # Try ANSI clear, fall back to printing newlines
        if sys.platform != "win32":
            os.system("clear" if os.name == "posix" else "cls")
        else:
            print("\n" * 3)
