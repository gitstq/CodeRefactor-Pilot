"""
File utility module.

Provides helper functions for file discovery, reading, and language detection
used throughout CodeRefactor Pilot.
"""

import os
import re
from pathlib import Path
from typing import Generator, List, Optional, Set, Tuple


# File extension to language mapping
LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
}

# Default directories to exclude from scanning
DEFAULT_EXCLUDE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".tox", ".eggs", "*.egg-info",
    ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "vendor", ".bundle", "coverage", ".nyc_output",
}

# Default file patterns to exclude
DEFAULT_EXCLUDE_PATTERNS = {
    "*.pyc", "*.pyo", "*.so", "*.dylib", "*.dll",
    ".DS_Store", "Thumbs.db",
}


def detect_language(file_path: str) -> Optional[str]:
    """Detect the programming language of a file based on its extension.

    Args:
        file_path: Path to the file.

    Returns:
        Language name string, or None if language cannot be detected.
    """
    ext = Path(file_path).suffix.lower()
    return LANGUAGE_MAP.get(ext)


def is_source_file(file_path: str) -> bool:
    """Check if a file is a recognized source code file.

    Args:
        file_path: Path to the file.

    Returns:
        True if the file has a recognized source code extension.
    """
    return detect_language(file_path) is not None


def should_exclude(file_path: str, exclude_dirs: Optional[Set[str]] = None,
                   exclude_patterns: Optional[Set[str]] = None) -> bool:
    """Check if a file or directory should be excluded from scanning.

    Args:
        file_path: Path to the file or directory.
        exclude_dirs: Set of directory names to exclude.
        exclude_patterns: Set of glob patterns to exclude.

    Returns:
        True if the file should be excluded.
    """
    path = Path(file_path)
    name = path.name

    # Check directory exclusion
    dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    for part in path.parts:
        if part in dirs:
            return True

    # Check pattern exclusion
    patterns = exclude_patterns or DEFAULT_EXCLUDE_PATTERNS
    for pattern in patterns:
        if _match_glob(name, pattern):
            return True

    # Skip hidden files (except we want to scan some dotfiles)
    if name.startswith(".") and name not in {".coderefactor-pilot.ini"}:
        return True

    return False


def _match_glob(name: str, pattern: str) -> bool:
    """Simple glob matching without using fnmatch for consistency.

    Supports * (any characters) and ? (single character).

    Args:
        name: File name to match.
        pattern: Glob pattern.

    Returns:
        True if the name matches the pattern.
    """
    # Convert glob pattern to regex
    regex = "^"
    for char in pattern:
        if char == "*":
            regex += ".*"
        elif char == "?":
            regex += "."
        elif char in ".+^${}()|[]\\":
            regex += "\\" + char
        else:
            regex += char
    regex += "$"

    try:
        return bool(re.match(regex, name))
    except re.error:
        return False


def discover_files(
    root_path: str,
    languages: Optional[List[str]] = None,
    exclude_dirs: Optional[Set[str]] = None,
    exclude_patterns: Optional[Set[str]] = None,
) -> Generator[str, None, None]:
    """Discover source files in a directory tree.

    Args:
        root_path: Root directory to scan.
        languages: List of languages to include. None means all supported.
        exclude_dirs: Set of directory names to exclude.
        exclude_patterns: Set of glob patterns to exclude.

    Yields:
        Paths to discovered source files.
    """
    root = Path(root_path)
    if not root.exists():
        return

    if root.is_file():
        if is_source_file(str(root)):
            lang = detect_language(str(root))
            if languages is None or lang in languages:
                yield str(root)
        return

    for dirpath, dirnames, filenames in os.walk(str(root)):
        # Filter out excluded directories in-place to prevent os.walk from descending
        dirnames[:] = [
            d for d in dirnames
            if not should_exclude(os.path.join(dirpath, d), exclude_dirs, exclude_patterns)
        ]

        for filename in sorted(filenames):
            file_path = os.path.join(dirpath, filename)
            if should_exclude(file_path, exclude_dirs, exclude_patterns):
                continue

            lang = detect_language(file_path)
            if lang is None:
                continue

            if languages is not None and lang not in languages:
                continue

            yield file_path


def read_file(file_path: str, encoding: str = "utf-8") -> Optional[str]:
    """Read file contents with encoding fallback.

    Tries UTF-8 first, then falls back to latin-1 which can read any byte sequence.

    Args:
        file_path: Path to the file.
        encoding: Preferred encoding.

    Returns:
        File contents as string, or None if file cannot be read.
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except (IOError, OSError, UnicodeDecodeError):
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except (IOError, OSError):
            return None


def get_file_lines(file_path: str) -> Optional[List[str]]:
    """Read file and return lines.

    Args:
        file_path: Path to the file.

    Returns:
        List of lines (without newlines), or None if file cannot be read.
    """
    content = read_file(file_path)
    if content is None:
        return None
    return content.splitlines()


def count_lines(content: str) -> int:
    """Count non-empty lines in content.

    Args:
        content: Source code content.

    Returns:
        Number of non-empty lines.
    """
    return sum(1 for line in content.splitlines() if line.strip())


def get_line(content: str, line_number: int) -> str:
    """Get a specific line from content (1-indexed).

    Args:
        content: Source code content.
        line_number: 1-indexed line number.

    Returns:
        The line content, or empty string if out of range.
    """
    lines = content.splitlines()
    if 1 <= line_number <= len(lines):
        return lines[line_number - 1]
    return ""


def get_context_lines(content: str, line_number: int, context: int = 2) -> List[Tuple[int, str]]:
    """Get context lines around a specific line.

    Args:
        content: Source code content.
        line_number: 1-indexed line number.
        context: Number of lines before and after.

    Returns:
        List of (line_number, line_content) tuples.
    """
    lines = content.splitlines()
    start = max(0, line_number - 1 - context)
    end = min(len(lines), line_number + context)
    result = []
    for i in range(start, end):
        result.append((i + 1, lines[i]))
    return result


def get_file_extension(file_path: str) -> str:
    """Get the file extension (lowercase, with dot).

    Args:
        file_path: Path to the file.

    Returns:
        Lowercase file extension including the dot.
    """
    return Path(file_path).suffix.lower()
