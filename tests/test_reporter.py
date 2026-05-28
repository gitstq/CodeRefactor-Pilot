"""
Tests for reporter modules.

Tests each reporter to ensure correct output generation.
"""

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coderefactor_pilot.rules.base import Issue, Severity, AnalysisResult
from coderefactor_pilot.reporter.json_reporter import JSONReporter
from coderefactor_pilot.reporter.html_reporter import HTMLReporter
from coderefactor_pilot.reporter.markdown_reporter import MarkdownReporter
from coderefactor_pilot.reporter.base import BaseReporter, Colors


def make_sample_result() -> AnalysisResult:
    """Create a sample AnalysisResult for testing.

    Returns:
        AnalysisResult with sample issues.
    """
    issues = [
        Issue(
            rule_id="CC001",
            rule_name="Cyclomatic Complexity",
            severity=Severity.HIGH,
            message="Function 'complex' has complexity 15",
            file_path="/src/module.py",
            line=10,
            code_snippet="def complex(x, y):",
            suggestion="Break into smaller functions",
            category="complexity",
            language="python",
        ),
        Issue(
            rule_id="SEC001",
            rule_name="Hardcoded Password",
            severity=Severity.CRITICAL,
            message="Hardcoded secret detected: 'password'",
            file_path="/src/config.py",
            line=5,
            code_snippet='password = "secret123"',
            suggestion="Use environment variables",
            category="security",
            language="python",
        ),
        Issue(
            rule_id="NM001",
            rule_name="Snake Case Naming",
            severity=Severity.LOW,
            message="Function 'BadFunc' should use snake_case",
            file_path="/src/module.py",
            line=20,
            code_snippet="def BadFunc():",
            suggestion="Rename to 'bad_func'",
            category="naming",
            language="python",
        ),
    ]

    return AnalysisResult(
        issues=issues,
        files_scanned=10,
        files_with_issues=3,
        scan_time=1.234,
        language_stats={
            "python": {"files": 8, "issues": 3},
            "javascript": {"files": 2, "issues": 0},
        },
    )


class TestJSONReporter(unittest.TestCase):
    """Test cases for the JSON reporter."""

    def test_generate_valid_json(self):
        """Test that generated output is valid JSON."""
        result = make_sample_result()
        reporter = JSONReporter()
        output = reporter.generate(result)

        # Should not raise
        parsed = json.loads(output)
        self.assertIsInstance(parsed, dict)

    def test_report_structure(self):
        """Test that the report has the expected structure."""
        result = make_sample_result()
        reporter = JSONReporter()
        output = reporter.generate(result)
        parsed = json.loads(output)

        self.assertIn("summary", parsed)
        self.assertIn("issues", parsed)
        self.assertIn("language_stats", parsed)

        summary = parsed["summary"]
        self.assertEqual(summary["files_scanned"], 10)
        self.assertEqual(summary["total_issues"], 3)
        self.assertEqual(summary["severity_breakdown"]["critical"], 1)
        self.assertEqual(summary["severity_breakdown"]["high"], 1)
        self.assertEqual(summary["severity_breakdown"]["low"], 1)

    def test_empty_result(self):
        """Test report with no issues."""
        result = AnalysisResult(
            issues=[],
            files_scanned=5,
            files_with_issues=0,
            scan_time=0.5,
        )
        reporter = JSONReporter()
        output = reporter.generate(result)
        parsed = json.loads(output)

        self.assertEqual(parsed["summary"]["total_issues"], 0)
        self.assertEqual(len(parsed["issues"]), 0)


class TestHTMLReporter(unittest.TestCase):
    """Test cases for the HTML reporter."""

    def test_generate_valid_html(self):
        """Test that generated output contains HTML structure."""
        result = make_sample_result()
        reporter = HTMLReporter()
        output = reporter.generate(result)

        self.assertIn("<!DOCTYPE html>", output)
        self.assertIn("<html", output)
        self.assertIn("</html>", output)
        self.assertIn("<head>", output)
        self.assertIn("<body>", output)

    def test_contains_issue_details(self):
        """Test that the HTML contains issue details."""
        result = make_sample_result()
        reporter = HTMLReporter()
        output = reporter.generate(result)

        self.assertIn("CC001", output)
        self.assertIn("SEC001", output)
        self.assertIn("NM001", output)
        self.assertIn("Cyclomatic Complexity", output)
        self.assertIn("Hardcoded Password", output)

    def test_contains_summary(self):
        """Test that the HTML contains summary information."""
        result = make_sample_result()
        reporter = HTMLReporter()
        output = reporter.generate(result)

        self.assertIn("10", output)  # files scanned
        self.assertIn("3", output)   # total issues

    def test_empty_result(self):
        """Test HTML report with no issues."""
        result = AnalysisResult(
            issues=[],
            files_scanned=5,
            files_with_issues=0,
            scan_time=0.5,
        )
        reporter = HTMLReporter()
        output = reporter.generate(result)

        self.assertIn("No issues found", output)


class TestMarkdownReporter(unittest.TestCase):
    """Test cases for the Markdown reporter."""

    def test_generate_markdown(self):
        """Test that generated output is Markdown format."""
        result = make_sample_result()
        reporter = MarkdownReporter()
        output = reporter.generate(result)

        self.assertIn("# CodeRefactor Pilot", output)
        self.assertIn("## Summary", output)
        self.assertIn("## Issues", output)

    def test_contains_issue_details(self):
        """Test that Markdown contains issue details."""
        result = make_sample_result()
        reporter = MarkdownReporter()
        output = reporter.generate(result)

        self.assertIn("CC001", output)
        self.assertIn("SEC001", output)
        self.assertIn("NM001", output)

    def test_contains_tables(self):
        """Test that Markdown contains tables."""
        result = make_sample_result()
        reporter = MarkdownReporter()
        output = reporter.generate(result)

        self.assertIn("| Metric | Value |", output)
        self.assertIn("| Severity | Count |", output)

    def test_empty_result(self):
        """Test Markdown report with no issues."""
        result = AnalysisResult(
            issues=[],
            files_scanned=5,
            files_with_issues=0,
            scan_time=0.5,
        )
        reporter = MarkdownReporter()
        output = reporter.generate(result)

        self.assertIn("No issues found", output)


class TestBaseReporter(unittest.TestCase):
    """Test cases for the base reporter."""

    def test_format_issue(self):
        """Test issue formatting."""
        issue = Issue(
            rule_id="TEST001",
            rule_name="Test Rule",
            severity=Severity.HIGH,
            message="This is a test issue",
            file_path="/test.py",
            line=42,
            code_snippet="x = 1",
            suggestion="Fix it",
            category="test",
            language="python",
        )
        reporter = BaseReporter(use_color=False)
        formatted = reporter.format_issue(issue)

        self.assertIn("TEST001", formatted)
        self.assertIn("Test Rule", formatted)
        self.assertIn("This is a test issue", formatted)
        self.assertIn("/test.py:42", formatted)

    def test_generate_summary(self):
        """Test summary generation."""
        result = make_sample_result()
        reporter = BaseReporter(use_color=False)
        summary = reporter.generate_summary(result)

        self.assertIn("Files scanned: 10", summary)
        self.assertIn("Total issues: 3", summary)
        self.assertIn("Severity breakdown:", summary)

    def test_colors_disable(self):
        """Test that colors can be disabled."""
        Colors.disable()
        self.assertEqual(Colors.RED, "")
        self.assertEqual(Colors.GREEN, "")
        self.assertEqual(Colors.RESET, "")


class TestSeverity(unittest.TestCase):
    """Test cases for Severity enum."""

    def test_from_string(self):
        """Test severity parsing from string."""
        self.assertEqual(Severity.from_string("low"), Severity.LOW)
        self.assertEqual(Severity.from_string("medium"), Severity.MEDIUM)
        self.assertEqual(Severity.from_string("high"), Severity.HIGH)
        self.assertEqual(Severity.from_string("critical"), Severity.CRITICAL)

    def test_from_string_case_insensitive(self):
        """Test case-insensitive severity parsing."""
        self.assertEqual(Severity.from_string("LOW"), Severity.LOW)
        self.assertEqual(Severity.from_string("High"), Severity.HIGH)

    def test_from_string_invalid(self):
        """Test that invalid severity raises ValueError."""
        with self.assertRaises(ValueError):
            Severity.from_string("invalid")

    def test_comparison(self):
        """Test severity comparison operators."""
        self.assertTrue(Severity.HIGH >= Severity.MEDIUM)
        self.assertTrue(Severity.CRITICAL > Severity.HIGH)
        self.assertTrue(Severity.LOW >= Severity.LOW)
        self.assertFalse(Severity.LOW > Severity.MEDIUM)


if __name__ == "__main__":
    unittest.main()
