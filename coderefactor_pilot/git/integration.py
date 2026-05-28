"""
Git integration module.

Provides functionality for integrating with Git repositories to analyze
changed files, staged files, and specific commit ranges.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Set


class GitIntegration:
    """Handles Git repository integration for CodeRefactor Pilot.

    Detects Git repositories, retrieves changed files, and supports
    various diff modes for targeted code review.

    Attributes:
        repo_root: Path to the Git repository root directory.
    """

    def __init__(self, repo_root: str = "."):
        """Initialize Git integration for a repository.

        Args:
            repo_root: Path to the repository root. Defaults to current directory.
        """
        self.repo_root = os.path.abspath(repo_root)
        self._is_git_repo = self._check_git_repo()

    def _check_git_repo(self) -> bool:
        """Check if the current directory is a Git repository.

        Returns:
            True if the directory is inside a Git repository.
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0 and result.stdout.strip() == "true"
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            return False

    @property
    def is_git_repo(self) -> bool:
        """Check if the path is a Git repository.

        Returns:
            True if the path is a Git repository.
        """
        return self._is_git_repo

    def get_repo_root(self) -> Optional[str]:
        """Get the root directory of the Git repository.

        Returns:
            Absolute path to the repository root, or None if not a repo.
        """
        if not self._is_git_repo:
            return None

        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            pass

        return None

    def get_staged_files(self) -> List[str]:
        """Get list of files that are staged for commit.

        Returns:
            List of absolute file paths that are staged.
        """
        if not self._is_git_repo:
            return []

        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                return [
                    os.path.join(self.repo_root, f)
                    for f in files if f.strip()
                ]
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            pass

        return []

    def get_unstaged_files(self) -> List[str]:
        """Get list of files with unstaged changes.

        Returns:
            List of absolute file paths with unstaged modifications.
        """
        if not self._is_git_repo:
            return []

        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACMR"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                return [
                    os.path.join(self.repo_root, f)
                    for f in files if f.strip()
                ]
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            pass

        return []

    def get_changed_files(self, include_staged: bool = True,
                          include_unstaged: bool = True) -> List[str]:
        """Get all changed files (staged and/or unstaged).

        Args:
            include_staged: Whether to include staged files.
            include_unstaged: Whether to include unstaged files.

        Returns:
            List of absolute file paths with changes.
        """
        files: Set[str] = set()

        if include_staged:
            files.update(self.get_staged_files())

        if include_unstaged:
            files.update(self.get_unstaged_files())

        return sorted(files)

    def get_files_in_commit_range(self, commit_range: str) -> List[str]:
        """Get files changed in a commit range.

        Args:
            commit_range: Git commit range (e.g., 'HEAD~5..HEAD', 'main..feature').

        Returns:
            List of absolute file paths changed in the range.
        """
        if not self._is_git_repo:
            return []

        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACMR", commit_range],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                return [
                    os.path.join(self.repo_root, f)
                    for f in files if f.strip()
                ]
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            pass

        return []

    def get_last_commit_files(self, count: int = 1) -> List[str]:
        """Get files changed in the last N commits.

        Args:
            count: Number of commits to look back.

        Returns:
            List of absolute file paths changed in the last N commits.
        """
        return self.get_files_in_commit_range(f"HEAD~{count}..HEAD")

    def get_branch_name(self) -> Optional[str]:
        """Get the current branch name.

        Returns:
            Current branch name, or None if not in a repo or detached HEAD.
        """
        if not self._is_git_repo:
            return None

        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                if branch != "HEAD":
                    return branch
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            pass

        return None

    def get_tracked_files(self) -> List[str]:
        """Get all files tracked by Git.

        Returns:
            List of absolute file paths tracked by Git.
        """
        if not self._is_git_repo:
            return []

        try:
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                return [
                    os.path.join(self.repo_root, f)
                    for f in files if f.strip()
                ]
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            pass

        return []

    def get_diff_for_file(self, file_path: str) -> str:
        """Get the diff for a specific file.

        Args:
            file_path: Path to the file.

        Returns:
            Unified diff string for the file.
        """
        if not self._is_git_repo:
            return ""

        # Make file path relative to repo root
        try:
            rel_path = os.path.relpath(file_path, self.repo_root)
        except ValueError:
            return ""

        try:
            # Get both staged and unstaged diff
            result = subprocess.run(
                ["git", "diff", "HEAD", "--", rel_path],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            pass

        return ""
