"""
JSON report generator.

Generates reports in JSON format for programmatic consumption.
"""

import json
from typing import Any, Dict

from coderefactor_pilot.reporter.base import BaseReporter
from coderefactor_pilot.rules.base import AnalysisResult


class JSONReporter(BaseReporter):
    """Generates reports in JSON format.

    Produces structured JSON output suitable for programmatic consumption,
    CI/CD integration, and further processing.

    Attributes:
        name: Format identifier.
        extension: Default file extension.
    """

    name = "json"
    extension = ".json"

    def generate(self, result: AnalysisResult) -> str:
        """Generate a JSON report from analysis results.

        Args:
            result: Analysis results to report.

        Returns:
            JSON-formatted report string.
        """
        report = self._build_report(result)
        return json.dumps(report, indent=2, ensure_ascii=False)

    def _build_report(self, result: AnalysisResult) -> Dict[str, Any]:
        """Build the report data structure.

        Args:
            result: Analysis results.

        Returns:
            Dictionary representation of the report.
        """
        report = {
            "summary": {
                "files_scanned": result.files_scanned,
                "files_with_issues": result.files_with_issues,
                "total_issues": len(result.issues),
                "scan_time_seconds": round(result.scan_time, 3),
                "severity_breakdown": result.severity_summary(),
                "category_breakdown": result.category_summary(),
            },
            "language_stats": result.language_stats,
            "issues": [issue.to_dict() for issue in result.issues],
        }

        return report
