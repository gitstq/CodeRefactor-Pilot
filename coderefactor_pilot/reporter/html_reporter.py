"""
HTML report generator.

Generates reports in HTML format with embedded CSS styling for
a polished, browser-viewable report.
"""

import html
from typing import List

from coderefactor_pilot.reporter.base import BaseReporter
from coderefactor_pilot.rules.base import AnalysisResult, Issue, Severity


class HTMLReporter(BaseReporter):
    """Generates reports in HTML format.

    Produces a self-contained HTML file with embedded CSS styling,
    suitable for sharing and viewing in any web browser.

    Attributes:
        name: Format identifier.
        extension: Default file extension.
    """

    name = "html"
    extension = ".html"

    # Severity to CSS class mapping
    SEVERITY_CLASSES = {
        Severity.LOW: "severity-low",
        Severity.MEDIUM: "severity-medium",
        Severity.HIGH: "severity-high",
        Severity.CRITICAL: "severity-critical",
    }

    def generate(self, result: AnalysisResult) -> str:
        """Generate an HTML report from analysis results.

        Args:
            result: Analysis results to report.

        Returns:
            Complete HTML document string.
        """
        parts = [
            self._generate_header(),
            self._generate_summary(result),
            self._generate_issues(result),
            self._generate_footer(),
        ]
        return "\n".join(parts)

    def _generate_header(self) -> str:
        """Generate the HTML header with embedded CSS.

        Returns:
            HTML header string with styles.
        """
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeRefactor Pilot - Code Review Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 {
            color: #1a1a2e;
            margin-bottom: 10px;
            font-size: 1.8em;
        }
        .subtitle { color: #666; margin-bottom: 30px; }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #1a1a2e;
        }
        .summary-card .label {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .severity-breakdown {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .severity-breakdown h2 {
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .severity-bar {
            display: flex;
            align-items: center;
            margin: 8px 0;
        }
        .severity-bar .label {
            width: 80px;
            font-weight: 500;
        }
        .severity-bar .bar {
            flex: 1;
            height: 24px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
            margin: 0 10px;
        }
        .severity-bar .bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }
        .severity-bar .count {
            width: 40px;
            text-align: right;
            font-weight: 500;
        }
        .severity-low .bar-fill { background: #4fc3f7; }
        .severity-low .label { color: #0288d1; }
        .severity-medium .bar-fill { background: #ffb74d; }
        .severity-medium .label { color: #f57c00; }
        .severity-high .bar-fill { background: #e57373; }
        .severity-high .label { color: #d32f2f; }
        .severity-critical .bar-fill { background: #b71c1c; }
        .severity-critical .label { color: #b71c1c; font-weight: bold; }
        .issues-section {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .issues-section h2 { margin-bottom: 15px; font-size: 1.2em; }
        .issue {
            border: 1px solid #eee;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #ccc;
        }
        .issue.severity-low { border-left-color: #4fc3f7; }
        .issue.severity-medium { border-left-color: #ffb74d; }
        .issue.severity-high { border-left-color: #e57373; }
        .issue.severity-critical { border-left-color: #b71c1c; }
        .issue-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .issue-rule {
            font-weight: 600;
            color: #1a1a2e;
        }
        .issue-severity {
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
        }
        .severity-low .issue-severity { background: #e1f5fe; color: #0288d1; }
        .severity-medium .issue-severity { background: #fff3e0; color: #f57c00; }
        .severity-high .issue-severity { background: #ffebee; color: #d32f2f; }
        .severity-critical .issue-severity { background: #b71c1c; color: white; }
        .issue-location {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .issue-message { margin-bottom: 8px; }
        .issue-code {
            background: #f5f5f5;
            border-radius: 4px;
            padding: 10px;
            font-family: 'Fira Code', 'Consolas', monospace;
            font-size: 0.85em;
            overflow-x: auto;
            white-space: pre-wrap;
            margin-bottom: 8px;
        }
        .issue-suggestion {
            background: #e8f5e9;
            border-radius: 4px;
            padding: 10px;
            font-size: 0.9em;
        }
        .issue-suggestion strong { color: #2e7d32; }
        .no-issues {
            text-align: center;
            padding: 40px;
            color: #4caf50;
            font-size: 1.2em;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #999;
            font-size: 0.85em;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>CodeRefactor Pilot</h1>
    <p class="subtitle">Code Review & Refactoring Report</p>"""

    def _generate_summary(self, result: AnalysisResult) -> str:
        """Generate the summary section of the HTML report.

        Args:
            result: Analysis results.

        Returns:
            HTML summary section string.
        """
        sev_summary = result.severity_summary()
        total = max(len(result.issues), 1)

        parts = [
            '<div class="summary-grid">',
            f'  <div class="summary-card"><div class="value">{result.files_scanned}</div><div class="label">Files Scanned</div></div>',
            f'  <div class="summary-card"><div class="value">{result.files_with_issues}</div><div class="label">Files with Issues</div></div>',
            f'  <div class="summary-card"><div class="value">{len(result.issues)}</div><div class="label">Total Issues</div></div>',
            f'  <div class="summary-card"><div class="value">{result.scan_time:.2f}s</div><div class="label">Scan Time</div></div>',
            '</div>',
            '<div class="severity-breakdown">',
            '  <h2>Severity Breakdown</h2>',
        ]

        for sev in Severity:
            count = sev_summary.get(sev.value, 0)
            pct = (count / total) * 100 if total > 0 else 0
            css_class = self.SEVERITY_CLASSES.get(sev, "")
            parts.append(
                f'  <div class="severity-bar {css_class}">'
                f'    <span class="label">{sev.value}</span>'
                f'    <div class="bar"><div class="bar-fill" style="width: {pct:.1f}%"></div></div>'
                f'    <span class="count">{count}</span>'
                f'  </div>'
            )

        parts.append('</div>')
        return "\n".join(parts)

    def _generate_issues(self, result: AnalysisResult) -> str:
        """Generate the issues section of the HTML report.

        Args:
            result: Analysis results.

        Returns:
            HTML issues section string.
        """
        if not result.issues:
            return (
                '<div class="issues-section">'
                '<div class="no-issues">No issues found! Code looks clean.</div>'
                '</div>'
            )

        parts = [
            '<div class="issues-section">',
            f'  <h2>Issues ({len(result.issues)})</h2>',
        ]

        for issue in result.issues:
            css_class = self.SEVERITY_CLASSES.get(issue.severity, "")
            parts.append(f'  <div class="issue {css_class}">')
            parts.append(f'    <div class="issue-header">')
            parts.append(f'      <span class="issue-rule">{html.escape(issue.rule_name)} ({html.escape(issue.rule_id)})</span>')
            parts.append(f'      <span class="issue-severity">{html.escape(issue.severity.value)}</span>')
            parts.append(f'    </div>')
            parts.append(f'    <div class="issue-location">{html.escape(issue.file_path)}:{issue.line}</div>')
            parts.append(f'    <div class="issue-message">{html.escape(issue.message)}</div>')

            if issue.code_snippet:
                parts.append(f'    <div class="issue-code">{html.escape(issue.code_snippet)}</div>')

            if issue.suggestion:
                parts.append(f'    <div class="issue-suggestion"><strong>Suggestion:</strong> {html.escape(issue.suggestion)}</div>')

            parts.append(f'  </div>')

        parts.append('</div>')
        return "\n".join(parts)

    def _generate_footer(self) -> str:
        """Generate the HTML footer.

        Returns:
            HTML footer string.
        """
        return (
            '<div class="footer">'
            'Generated by CodeRefactor Pilot'
            '</div>'
            '</div>'
            '</body>'
            '</html>'
        )
