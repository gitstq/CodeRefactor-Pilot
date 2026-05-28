"""
CLI entry point for CodeRefactor Pilot.

Provides the command-line interface for running code analysis,
managing configuration, and viewing results.
"""

import argparse
import os
import sys
import time
from typing import List, Optional

# Add parent directory to path for direct execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coderefactor_pilot import __version__
from coderefactor_pilot.utils.config import Config
from coderefactor_pilot.utils.file_utils import (
    discover_files, detect_language, read_file, LANGUAGE_MAP,
)
from coderefactor_pilot.analyzer.python_analyzer import PythonAnalyzer
from coderefactor_pilot.analyzer.javascript_analyzer import JavaScriptAnalyzer
from coderefactor_pilot.analyzer.typescript_analyzer import TypeScriptAnalyzer
from coderefactor_pilot.analyzer.go_analyzer import GoAnalyzer
from coderefactor_pilot.analyzer.base import BaseAnalyzer
from coderefactor_pilot.rules.base import Severity, AnalysisResult
from coderefactor_pilot.reporter.base import BaseReporter, Colors
from coderefactor_pilot.reporter.json_reporter import JSONReporter
from coderefactor_pilot.reporter.html_reporter import HTMLReporter
from coderefactor_pilot.reporter.markdown_reporter import MarkdownReporter
from coderefactor_pilot.git.integration import GitIntegration
from coderefactor_pilot.tui.dashboard import Dashboard


# Analyzer registry mapping languages to analyzer classes
ANALYZER_MAP = {
    "python": PythonAnalyzer,
    "javascript": JavaScriptAnalyzer,
    "typescript": TypeScriptAnalyzer,
    "go": GoAnalyzer,
}

# Reporter registry mapping format names to reporter classes
REPORTER_MAP = {
    "terminal": None,  # Uses default terminal output
    "json": JSONReporter,
    "html": HTMLReporter,
    "markdown": MarkdownReporter,
}


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="coderefactor-pilot",
        description="CodeRefactor Pilot - AI-Powered Code Review & Intelligent Refactoring Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  coderefactor-pilot scan ./src                    Scan a directory
  coderefactor-pilot scan --diff                   Scan git changes only
  coderefactor-pilot scan --lang python ./src      Scan Python files only
  coderefactor-pilot scan --severity high ./src    Show high+ severity issues
  coderefactor-pilot scan --report json --output report.json ./src
  coderefactor-pilot scan --ai --ai-backend openai ./src
  coderefactor-pilot rules                         List all available rules
  coderefactor-pilot version                       Show version info
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan source code for issues")
    scan_parser.add_argument("path", nargs="?", default=".", help="Path to scan (default: current directory)")
    scan_parser.add_argument("--diff", action="store_true", help="Only scan git changed files")
    scan_parser.add_argument("--diff-range", type=str, default="", help="Git commit range to scan (e.g., HEAD~5..HEAD)")
    scan_parser.add_argument("--lang", "--language", type=str, default="", help="Target language (python, javascript, typescript, go)")
    scan_parser.add_argument("--severity", type=str, default="low", choices=["low", "medium", "high", "critical"], help="Minimum severity level (default: low)")
    scan_parser.add_argument("--report", type=str, default="terminal", choices=["terminal", "json", "html", "markdown"], help="Report format (default: terminal)")
    scan_parser.add_argument("--output", "-o", type=str, default="", help="Output file path")
    scan_parser.add_argument("--ai", action="store_true", help="Enable AI refactoring suggestions")
    scan_parser.add_argument("--ai-backend", type=str, default="openai", choices=["openai", "claude", "gemini", "local"], help="AI backend to use")
    scan_parser.add_argument("--ai-key", type=str, default="", help="API key for AI backend")
    scan_parser.add_argument("--ai-model", type=str, default="", help="AI model to use")
    scan_parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    scan_parser.add_argument("--interactive", "-i", action="store_true", help="Show interactive TUI dashboard")
    scan_parser.add_argument("--exclude", type=str, default="", help="Comma-separated directories to exclude")
    scan_parser.add_argument("--config", type=str, default="", help="Path to config file")

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--init", action="store_true", help="Initialize global configuration")
    config_parser.add_argument("--show", action="store_true", help="Show current configuration")
    config_parser.add_argument("--set", type=str, nargs=2, metavar=("KEY", "VALUE"), help="Set a configuration value")
    config_parser.add_argument("--get", type=str, metavar="KEY", help="Get a configuration value")

    # Rules command
    rules_parser = subparsers.add_parser("rules", help="List all available rules")
    rules_parser.add_argument("--category", type=str, default="", help="Filter by category")
    rules_parser.add_argument("--lang", type=str, default="", help="Filter by language")

    # Version command
    subparsers.add_parser("version", help="Show version information")

    return parser


def get_analyzer(language: str, config_dict: dict) -> Optional[BaseAnalyzer]:
    """Get the appropriate analyzer for a language.

    Args:
        language: Programming language name.
        config_dict: Configuration dictionary.

    Returns:
        Analyzer instance, or None if language is not supported.
    """
    analyzer_class = ANALYZER_MAP.get(language)
    if analyzer_class:
        return analyzer_class(config=config_dict)
    return None


def get_reporter(format_name: str, use_color: bool = True) -> BaseReporter:
    """Get the appropriate reporter for a format.

    Args:
        format_name: Report format name.
        use_color: Whether to use colored output.

    Returns:
        Reporter instance.
    """
    reporter_class = REPORTER_MAP.get(format_name)

    if reporter_class is None:
        # Terminal reporter (built-in basic reporter)
        return BaseReporter(use_color=use_color)

    return reporter_class(use_color=use_color)


def cmd_scan(args: argparse.Namespace) -> int:
    """Execute the scan command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for issues found, 2 for errors).
    """
    config = Config(project_root=args.path if os.path.isdir(args.path) else os.path.dirname(args.path or "."))

    use_color = not args.no_color and sys.stdout.isatty()

    # Build config dict for rules
    config_dict = {
        "max_line_length": config.getint("scan", "max_line_length", 120),
        "max_function_length": config.getint("scan", "max_function_length", 50),
        "max_file_length": config.getint("scan", "max_file_length", 500),
        "max_parameters": config.getint("scan", "max_parameters", 7),
        "max_complexity": config.getint("scan", "max_complexity", 10),
        "max_cognitive_complexity": config.getint("scan", "max_cognitive_complexity", 15),
        "max_nesting_depth": config.getint("scan", "max_nesting_depth", 4),
        "min_duplicate_lines": config.getint("scan", "min_duplicate_lines", 6),
    }

    # Determine files to scan
    file_paths: List[str] = []
    scan_path = args.path or "."

    if not os.path.exists(scan_path):
        print(f"Error: Path '{scan_path}' does not exist.", file=sys.stderr)
        return 2

    if args.diff or args.diff_range:
        # Git-based scanning
        git = GitIntegration(scan_path)
        if not git.is_git_repo:
            print("Error: Not a Git repository. Cannot use --diff mode.", file=sys.stderr)
            return 2

        if args.diff_range:
            file_paths = git.get_files_in_commit_range(args.diff_range)
        else:
            file_paths = git.get_changed_files()

        if not file_paths:
            print("No changed files found.")
            return 0

        print(f"Found {len(file_paths)} changed file(s) to scan.")
    else:
        # Regular directory scanning
        if os.path.isfile(scan_path):
            file_paths = [scan_path]
        else:
            languages = [args.lang] if args.lang else None
            exclude_dirs = set(args.exclude.split(",")) if args.exclude else None
            file_paths = list(discover_files(scan_path, languages=languages, exclude_dirs=exclude_dirs))

    if not file_paths:
        print("No files found to scan.")
        return 0

    # Filter by language if specified
    if args.lang:
        file_paths = [f for f in file_paths if detect_language(f) == args.lang]

    if not file_paths:
        print(f"No {args.lang} files found.", file=sys.stderr)
        return 0

    # Group files by language and create analyzers
    lang_files: dict = {}
    for fp in file_paths:
        lang = detect_language(fp)
        if lang:
            if lang not in lang_files:
                lang_files[lang] = []
            lang_files[lang].append(fp)

    # Run analysis
    all_issues = []
    total_files = 0
    files_with_issues = 0
    start_time = time.time()

    is_machine_readable = args.report in ("json", "html", "markdown")
    out = sys.stderr if is_machine_readable else sys.stdout

    print(f"\nScanning {len(file_paths)} file(s)...", file=out)

    for lang, files in sorted(lang_files.items()):
        analyzer = get_analyzer(lang, config_dict)
        if analyzer is None:
            print(f"  Skipping {len(files)} {lang} file(s) (no analyzer available)", file=out)
            continue

        print(f"  Analyzing {len(files)} {lang} file(s)...", file=out)

        for i, fp in enumerate(files):
            if use_color:
                Dashboard.show_progress(total_files + i + 1, len(file_paths), fp)

            issues = analyzer.analyze(fp)
            all_issues.extend(issues)

            if issues:
                files_with_issues += 1

        total_files += len(files)

    elapsed = time.time() - start_time

    # Build result
    min_severity = Severity.from_string(args.severity)
    filtered_issues = [i for i in all_issues if i.severity >= min_severity]

    # Build language stats
    lang_stats: dict = {}
    for lang, files in lang_files.items():
        lang_issues = [i for i in filtered_issues if i.language == lang]
        lang_stats[lang] = {
            "files": len(files),
            "issues": len(lang_issues),
        }

    result = AnalysisResult(
        issues=filtered_issues,
        files_scanned=total_files,
        files_with_issues=files_with_issues,
        scan_time=elapsed,
        language_stats=lang_stats,
    )

    # AI suggestions (if enabled)
    if args.ai and filtered_issues:
        print("\n  Generating AI suggestions...", file=out)
        _apply_ai_suggestions(result, args)

    # Generate report
    reporter = get_reporter(args.report, use_color=use_color)

    if args.report == "terminal":
        # Custom terminal output
        _print_terminal_report(result, use_color)
    else:
        report_content = reporter.generate(result)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report_content)
            print(f"\nReport saved to: {args.output}")
        else:
            print("\n" + report_content)

    # Interactive mode
    if args.interactive and filtered_issues:
        dashboard = Dashboard(result, use_color=use_color)
        dashboard.show_summary()
        dashboard.show_issues()

    # Exit code: 1 if issues found, 0 if clean
    return 1 if filtered_issues else 0


def _print_terminal_report(result: AnalysisResult, use_color: bool) -> None:
    """Print the terminal-formatted report.

    Args:
        result: Analysis results.
        use_color: Whether to use colored output.
    """
    if not use_color:
        Colors.disable()

    print()
    print(f"  {Colors.BOLD}CodeRefactor Pilot - Scan Results{Colors.RESET}")
    print(f"  {'=' * 55}")
    print(f"  Files scanned:     {result.files_scanned}")
    print(f"  Files with issues: {result.files_with_issues}")
    print(f"  Total issues:      {len(result.issues)}")
    print(f"  Scan time:         {result.scan_time:.3f}s")

    # Severity summary
    sev_summary = result.severity_summary()
    print()
    print(f"  {Colors.BOLD}Severity Summary:{Colors.RESET}")
    for sev in Severity:
        count = sev_summary.get(sev.value, 0)
        color = Colors.severity_color(sev)
        label = sev.value.upper().ljust(12)
        print(f"    {color}{label}{Colors.RESET} {count}")

    # Issues
    if result.issues:
        print()
        print(f"  {Colors.BOLD}Issues:{Colors.RESET}")
        print(f"  {'-' * 55}")

        # Group by file
        by_file: dict = {}
        for issue in result.issues:
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)

        for file_path, issues in sorted(by_file.items()):
            print()
            print(f"  {Colors.BOLD}{Colors.UNDERLINE}{file_path}{Colors.RESET} ({len(issues)} issue(s))")

            for issue in issues:
                print()
                print(f"    {Colors.severity_color(issue.severity)}[{issue.severity.value.upper()}]{Colors.RESET} "
                      f"{Colors.BOLD}{issue.rule_name}{Colors.RESET} ({issue.rule_id}) - Line {issue.line}")
                print(f"    {issue.message}")

                if issue.code_snippet:
                    print(f"    {Colors.DIM}{issue.code_snippet}{Colors.RESET}")

                if issue.suggestion:
                    print(f"    {Colors.GREEN}>> {issue.suggestion}{Colors.RESET}")

    print()
    if result.issues:
        print(f"  {Colors.BOLD}Scan complete: {len(result.issues)} issue(s) found.{Colors.RESET}")
    else:
        print(f"  {Colors.GREEN}{Colors.BOLD}Scan complete: No issues found!{Colors.RESET}")
    print()


def _apply_ai_suggestions(result: AnalysisResult, args: argparse.Namespace) -> None:
    """Apply AI-generated suggestions to issues.

    Args:
        result: Analysis results with issues.
        args: Command-line arguments for AI configuration.
    """
    try:
        if args.ai_backend == "openai":
            from coderefactor_pilot.ai.openai_backend import OpenAIBackend
            backend = OpenAIBackend(
                api_key=args.ai_key,
                model=args.ai_model or "gpt-4",
            )
        elif args.ai_backend == "claude":
            from coderefactor_pilot.ai.claude_backend import ClaudeBackend
            backend = ClaudeBackend(
                api_key=args.ai_key,
                model=args.ai_model or "claude-3-5-sonnet-20241022",
            )
        elif args.ai_backend == "gemini":
            from coderefactor_pilot.ai.gemini_backend import GeminiBackend
            backend = GeminiBackend(
                api_key=args.ai_key,
                model=args.ai_model or "gemini-pro",
            )
        elif args.ai_backend == "local":
            from coderefactor_pilot.ai.local_backend import LocalBackend
            backend = LocalBackend(
                model=args.ai_model or "codellama",
            )
        else:
            print(f"  Unknown AI backend: {args.ai_backend}")
            return

        # Only request suggestions for high-severity issues to save API calls
        high_priority = [i for i in result.issues if i.severity.value in ("high", "critical")]
        if not high_priority:
            high_priority = result.issues[:5]  # Limit to first 5 issues

        for issue in high_priority:
            try:
                suggestion = backend.get_suggestion(issue.to_dict(), issue.code_snippet)
                if suggestion and not suggestion.startswith("[AI Error]"):
                    issue.suggestion = suggestion
                    print(f"    AI suggestion for {issue.rule_id}: OK")
            except Exception as e:
                print(f"    AI suggestion for {issue.rule_id}: Failed - {e}")

    except ImportError as e:
        print(f"  AI backend error: {e}")


def cmd_config(args: argparse.Namespace) -> int:
    """Execute the config command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code.
    """
    if args.init:
        config = Config.init_global_config()
        print("Global configuration initialized at: ~/.coderefactor-pilot/config.ini")
        return 0

    config = Config()

    if args.show:
        print("Current configuration:")
        print("-" * 50)
        for section, options in config.to_dict().items():
            print(f"\n  [{section}]")
            for key, value in options.items():
                # Mask API keys
                if "key" in key.lower() and value:
                    display_value = value[:4] + "***" if len(value) > 4 else "***"
                else:
                    display_value = value
                print(f"    {key} = {display_value}")
        print()
        return 0

    if args.set:
        key, value = args.set
        # Try to determine section from key
        section = "general"
        if key.startswith("ai_"):
            section = "ai"
            key = key[3:]
        elif key.startswith("scan_"):
            section = "scan"
            key = key[5:]
        elif key.startswith("report_"):
            section = "report"
            key = key[7:]

        config.set(section, key, value)
        config.save_global()
        print(f"Set {section}.{key} = {value}")
        return 0

    if args.get:
        key = args.get
        section = "general"
        if "." in key:
            section, key = key.split(".", 1)
        value = config.get(section, key)
        print(f"{section}.{key} = {value}")
        return 0

    print("Use --init, --show, --set, or --get. See --help for details.")
    return 0


def cmd_rules(args: argparse.Namespace) -> int:
    """Execute the rules command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code.
    """
    config_dict = {}
    analyzers = []

    # Create analyzers for all supported languages
    for lang, analyzer_class in ANALYZER_MAP.items():
        if args.lang and lang != args.lang:
            continue
        analyzers.append(analyzer_class(config=config_dict))

    # Collect all rules
    all_rules = []
    seen_ids = set()
    for analyzer in analyzers:
        for rule_info in analyzer.list_rules():
            if rule_info["id"] not in seen_ids:
                seen_ids.add(rule_info["id"])
                all_rules.append(rule_info)

    # Filter by category
    if args.category:
        all_rules = [r for r in all_rules if r["category"] == args.category]

    if not all_rules:
        print("No rules found matching the specified filters.")
        return 0

    # Display rules
    use_color = sys.stdout.isatty()
    if not use_color:
        Colors.disable()

    print(f"\n  {Colors.BOLD}Available Rules ({len(all_rules)}){Colors.RESET}")
    print(f"  {'=' * 70}")
    print(f"  {'ID':<8} {'Name':<30} {'Severity':<10} {'Category':<15} {'Languages'}")
    print(f"  {'-' * 70}")

    for rule in sorted(all_rules, key=lambda r: (r["category"], r["id"])):
        sev = rule["severity"]
        color = Colors.severity_color(Severity.from_string(sev)) if use_color else ""
        reset = Colors.RESET if use_color else ""
        print(
            f"  {rule['id']:<8} {rule['name']:<30} "
            f"{color}{sev:<10}{reset} {rule['category']:<15} {rule['languages']}"
        )

    print()

    return 0


def cmd_version(args: argparse.Namespace) -> int:
    """Execute the version command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code.
    """
    print(f"\n  CodeRefactor Pilot v{__version__}")
    print(f"  Python {sys.version.split()[0]}")
    print(f"  Zero-dependency code review & refactoring engine")
    print()
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv).

    Returns:
        Exit code.
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "scan":
        return cmd_scan(args)
    elif args.command == "config":
        return cmd_config(args)
    elif args.command == "rules":
        return cmd_rules(args)
    elif args.command == "version":
        return cmd_version(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
