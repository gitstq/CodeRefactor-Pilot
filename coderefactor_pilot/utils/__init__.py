"""
Utility package for CodeRefactor Pilot.

Provides configuration management and file utility functions.
"""

from coderefactor_pilot.utils.config import Config, GLOBAL_CONFIG_DIR, GLOBAL_CONFIG_FILE
from coderefactor_pilot.utils.file_utils import (
    detect_language,
    discover_files,
    get_file_lines,
    get_line,
    get_context_lines,
    is_source_file,
    read_file,
    should_exclude,
    LANGUAGE_MAP,
)

__all__ = [
    "Config",
    "GLOBAL_CONFIG_DIR",
    "GLOBAL_CONFIG_FILE",
    "detect_language",
    "discover_files",
    "get_file_lines",
    "get_line",
    "get_context_lines",
    "is_source_file",
    "read_file",
    "should_exclude",
    "LANGUAGE_MAP",
]
