"""
Configuration management module.

Handles loading, saving, and accessing configuration settings
for CodeRefactor Pilot. Configuration is stored in INI format
and supports both global and project-level settings.
"""

import configparser
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_CONFIG = {
    "scan": {
        "max_line_length": "120",
        "max_function_length": "50",
        "max_file_length": "500",
        "max_parameters": "7",
        "max_complexity": "10",
        "max_cognitive_complexity": "15",
        "max_nesting_depth": "4",
        "min_duplicate_lines": "6",
    },
    "ai": {
        "backend": "openai",
        "model": "gpt-4",
        "api_key": "",
        "base_url": "",
        "max_tokens": "2048",
        "temperature": "0.3",
        "batch_size": "5",
        "delay_between_requests": "1.0",
    },
    "report": {
        "format": "terminal",
        "output": "",
        "include_context": "true",
        "color": "true",
    },
    "general": {
        "languages": "python,javascript,typescript,go",
        "exclude_dirs": ".git,__pycache__,node_modules,.venv,venv,dist,build",
        "exclude_files": "*.pyc,*.pyo,.DS_Store",
        "severity": "low",
    },
}

# Global configuration directory
GLOBAL_CONFIG_DIR = Path.home() / ".coderefactor-pilot"
GLOBAL_CONFIG_FILE = GLOBAL_CONFIG_DIR / "config.ini"


class Config:
    """Manages configuration for CodeRefactor Pilot.

    Supports layered configuration:
    1. Default built-in values
    2. Global user config (~/.coderefactor-pilot/config.ini)
    3. Project-level config (.coderefactor-pilot.ini in project root)
    4. CLI arguments (handled separately in cli.py)

    Attributes:
        config_dir: Directory for global configuration files.
        config_file: Path to the global configuration file.
    """

    def __init__(self, project_root: Optional[str] = None):
        """Initialize Config with optional project root.

        Args:
            project_root: Path to the project root directory.
                          If provided, project-level config will be loaded.
        """
        self._parser = configparser.ConfigParser()
        self._project_root = project_root
        self._project_config_file = None

        # Set all default values
        for section, options in DEFAULT_CONFIG.items():
            self._parser[section] = options

        # Load global config if exists
        self._load_global_config()

        # Load project config if exists
        if project_root:
            self._load_project_config(project_root)

    def _load_global_config(self) -> None:
        """Load global configuration from user home directory."""
        if GLOBAL_CONFIG_FILE.exists():
            try:
                self._parser.read(str(GLOBAL_CONFIG_FILE))
            except configparser.Error:
                pass  # Silently ignore corrupt config

    def _load_project_config(self, project_root: str) -> None:
        """Load project-level configuration.

        Args:
            project_root: Path to the project root directory.
        """
        root = Path(project_root)
        # Check multiple possible config file names
        for config_name in [".coderefactor-pilot.ini", "setup.cfg"]:
            config_path = root / config_name
            if config_path.exists():
                try:
                    self._parser.read(str(config_path))
                    self._project_config_file = config_path
                    break
                except configparser.Error:
                    pass

    def get(self, section: str, key: str, fallback: Optional[str] = None) -> str:
        """Get a configuration value.

        Args:
            section: Configuration section name.
            key: Configuration key name.
            fallback: Fallback value if key is not found.

        Returns:
            The configuration value as a string.
        """
        return self._parser.get(section, key, fallback=fallback)

    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Get a configuration value as an integer.

        Args:
            section: Configuration section name.
            key: Configuration key name.
            fallback: Fallback value if key is not found or not an integer.

        Returns:
            The configuration value as an integer.
        """
        try:
            return self._parser.getint(section, key, fallback=fallback)
        except (configparser.Error, ValueError):
            return fallback

    def getfloat(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get a configuration value as a float.

        Args:
            section: Configuration section name.
            key: Configuration key name.
            fallback: Fallback value if key is not found or not a float.

        Returns:
            The configuration value as a float.
        """
        try:
            return self._parser.getfloat(section, key, fallback=fallback)
        except (configparser.Error, ValueError):
            return fallback

    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get a configuration value as a boolean.

        Args:
            section: Configuration section name.
            key: Configuration key name.
            fallback: Fallback value if key is not found.

        Returns:
            The configuration value as a boolean.
        """
        try:
            return self._parser.getboolean(section, key, fallback=fallback)
        except (configparser.Error, ValueError):
            return fallback

    def getlist(self, section: str, key: str, fallback: Optional[list] = None) -> list:
        """Get a configuration value as a list (comma-separated).

        Args:
            section: Configuration section name.
            key: Configuration key name.
            fallback: Fallback value if key is not found.

        Returns:
            The configuration value as a list of strings.
        """
        value = self.get(section, key, "")
        if not value:
            return fallback or []
        return [item.strip() for item in value.split(",") if item.strip()]

    def set(self, section: str, key: str, value: str) -> None:
        """Set a configuration value.

        Args:
            section: Configuration section name.
            key: Configuration key name.
            value: Value to set.
        """
        if not self._parser.has_section(section):
            self._parser.add_section(section)
        self._parser.set(section, key, value)

    def save_global(self) -> None:
        """Save current configuration to global config file."""
        GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(str(GLOBAL_CONFIG_FILE), "w", encoding="utf-8") as f:
            self._parser.write(f)

    def save_project(self, project_root: Optional[str] = None) -> None:
        """Save current configuration to project-level config file.

        Args:
            project_root: Path to project root. Uses initialized root if not provided.
        """
        root = Path(project_root or self._project_root or ".")
        config_path = root / ".coderefactor-pilot.ini"
        with open(str(config_path), "w", encoding="utf-8") as f:
            self._parser.write(f)

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        """Convert configuration to a dictionary.

        Returns:
            Dictionary representation of all configuration sections.
        """
        result = {}
        for section in self._parser.sections():
            result[section] = dict(self._parser[section])
        return result

    @classmethod
    def init_global_config(cls) -> "Config":
        """Initialize and save a new global configuration with defaults.

        Returns:
            A new Config instance with default values saved to disk.
        """
        config = cls()
        config.save_global()
        return config
