"""
Code duplication detection rules.

Detects duplicated code blocks using AST-based comparison for Python
and text-based similarity analysis for other languages.
"""

import ast
import hashlib
import re
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from coderefactor_pilot.rules.base import BaseRule, Issue, Severity


class DuplicateCodeBlockRule(BaseRule):
    """Detects duplicated code blocks within a file.

    Uses AST-based normalization for Python code and text-based
    similarity for other languages. Identifies blocks of code
    that are structurally similar.

    Minimum duplicate lines is configurable via 'min_duplicate_lines' (default: 6).
    """

    id = "DP001"
    name = "Duplicate Code Blocks"
    description = "Detects duplicated code blocks that should be extracted into shared functions."
    severity = Severity.MEDIUM
    category = "duplication"
    languages = ["python", "javascript", "typescript", "go"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for duplicated blocks.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        min_lines = self.get_config("min_duplicate_lines", 6)

        if language == "python":
            return self._check_python(content, file_path, min_lines)
        else:
            return self._check_generic(content, file_path, language, min_lines)

    def _check_python(self, content: str, file_path: str, min_lines: int) -> List[Issue]:
        """Check Python code for duplicated blocks using AST.

        Args:
            content: Python source code.
            file_path: Path to the file.
            min_lines: Minimum number of lines for a block to be considered duplicate.

        Returns:
            List of issues found.
        """
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues

        lines = content.splitlines()

        # Extract function bodies as AST dumps
        function_blocks: List[Tuple[str, int, int, str]] = []  # (hash, start, end, name)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get the function body (excluding decorator and signature)
                body_start = node.body[0].lineno if node.body else node.lineno
                body_end = node.end_lineno or body_start

                if body_end - body_start + 1 < min_lines:
                    continue

                # Normalize and hash the function body AST
                body_text = "\n".join(lines[body_start - 1:body_end])
                normalized = self._normalize_python_code(body_text)
                code_hash = hashlib.md5(normalized.encode()).hexdigest()

                function_blocks.append((code_hash, body_start, body_end, node.name))

        # Find duplicates
        hash_groups: Dict[str, List[Tuple[int, int, str]]] = defaultdict(list)
        for code_hash, start, end, name in function_blocks:
            hash_groups[code_hash].append((start, end, name))

        reported_hashes: Set[str] = set()
        for code_hash, group in hash_groups.items():
            if len(group) > 1 and code_hash not in reported_hashes:
                reported_hashes.add(code_hash)
                # Report the first occurrence as the original
                orig_start, orig_end, orig_name = group[0]
                dup_names = [name for _, _, name in group[1:]]
                snippet = lines[orig_start - 1] if orig_start <= len(lines) else ""

                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message=(
                        f"Duplicated code detected: function '{orig_name}' has identical "
                        f"structure to function(s): {', '.join(dup_names)}. "
                        f"Consider extracting shared logic."
                    ),
                    file_path=file_path,
                    line=orig_start,
                    end_line=orig_end,
                    code_snippet=snippet.strip(),
                    suggestion="Extract the shared logic into a common helper function.",
                    category=self.category,
                    language="python",
                ))

        return issues

    def _normalize_python_code(self, code: str) -> str:
        """Normalize Python code for comparison.

        Removes variable names, string literals, and comments,
        keeping only the structural elements.

        Args:
            code: Python source code.

        Returns:
            Normalized code string.
        """
        # Remove comments
        code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)

        # Remove string literals
        code = re.sub(r'"""[\s\S]*?"""', '""', code)
        code = re.sub(r"'''[\s\S]*?'''", "''", code)
        code = re.sub(r'"[^"]*"', '""', code)
        code = re.sub(r"'[^']*'", "''", code)

        # Normalize variable names to a common placeholder
        # Replace identifiers (word characters) with a generic token
        code = re.sub(r"\b[a-zA-Z_]\w*\b", "V", code)

        # Normalize numbers
        code = re.sub(r"\b\d+\.?\d*\b", "N", code)

        # Normalize whitespace
        code = re.sub(r"\s+", " ", code).strip()

        return code

    def _check_generic(self, content: str, file_path: str, language: str,
                       min_lines: int) -> List[Issue]:
        """Check non-Python code for duplicated blocks.

        Uses sliding window approach to find similar code blocks.

        Args:
            content: Source code content.
            file_path: Path to the file.
            language: Programming language.
            min_lines: Minimum number of lines for a block to be considered duplicate.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()

        # Filter out empty lines and comments
        code_lines: List[Tuple[int, str]] = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith("//") and not stripped.startswith("*"):
                code_lines.append((i + 1, stripped))

        if len(code_lines) < min_lines * 2:
            return issues

        # Sliding window to find duplicate blocks
        block_size = min_lines
        seen_blocks: Dict[str, List[int]] = defaultdict(list)

        for start_idx in range(len(code_lines) - block_size + 1):
            block = code_lines[start_idx:start_idx + block_size]
            # Normalize the block
            normalized = self._normalize_generic_block(block)
            block_hash = hashlib.md5(normalized.encode()).hexdigest()
            line_num = block[0][0]

            seen_blocks[block_hash].append(line_num)

        # Report duplicates
        reported_hashes: Set[str] = set()
        for block_hash, occurrences in seen_blocks.items():
            if len(occurrences) > 1 and block_hash not in reported_hashes:
                reported_hashes.add(block_hash)
                first_line = occurrences[0]
                dup_lines = occurrences[1:]
                snippet = lines[first_line - 1] if first_line <= len(lines) else ""

                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message=(
                        f"Duplicated code block found at lines {first_line} "
                        f"and {', '.join(str(l) for l in dup_lines[:3])}. "
                        f"Consider extracting into a shared function."
                    ),
                    file_path=file_path,
                    line=first_line,
                    code_snippet=snippet.strip(),
                    suggestion="Extract the duplicated block into a reusable function.",
                    category=self.category,
                    language=language,
                ))

        return issues

    def _normalize_generic_block(self, block: List[Tuple[int, str]]) -> str:
        """Normalize a code block for comparison.

        Removes string literals, numbers, and normalizes whitespace.

        Args:
            block: List of (line_number, line_content) tuples.

        Returns:
            Normalized block string.
        """
        normalized_lines = []
        for _, line in block:
            # Remove string literals
            line = re.sub(r'"[^"]*"', '""', line)
            line = re.sub(r"'[^']*'", "''", line)
            # Remove numbers
            line = re.sub(r"\b\d+\.?\d*\b", "0", line)
            # Normalize whitespace
            line = re.sub(r"\s+", " ", line).strip()
            normalized_lines.append(line)

        return "\n".join(normalized_lines)


class SimilarFunctionRule(BaseRule):
    """Detects functions that are structurally similar but not identical.

    Uses normalized AST comparison to find functions that have the same
    structure but differ in variable names or literal values.
    """

    id = "DP002"
    name = "Similar Functions"
    description = "Detects functions with similar structure that may be refactored."
    severity = Severity.LOW
    category = "duplication"
    languages = ["python"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check for structurally similar Python functions.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        if language != "python":
            return []

        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues

        lines = content.splitlines()

        # Collect function signatures and body structures
        functions: List[Tuple[str, int, str, str]] = []  # (sig_hash, line, name, body_text)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Get signature structure
                sig = self._get_signature_structure(node)
                sig_hash = hashlib.md5(sig.encode()).hexdigest()

                # Get body structure (normalized)
                body_lines = lines[node.lineno:node.end_lineno]
                body_text = "\n".join(body_lines)
                normalized_body = self._normalize_for_similarity(body_text)

                functions.append((sig_hash, node.lineno, node.name, normalized_body))

        # Compare functions with similar signatures
        sig_groups: Dict[str, List[Tuple[int, str, str]]] = defaultdict(list)
        for sig_hash, line_num, name, body in functions:
            sig_groups[sig_hash].append((line_num, name, body))

        reported: Set[str] = set()
        for sig_hash, group in sig_groups.items():
            if len(group) < 2:
                continue

            # Compare body similarity
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    line_i, name_i, body_i = group[i]
                    line_j, name_j, body_j = group[j]

                    similarity = self._compute_similarity(body_i, body_j)
                    if similarity > 0.7:  # 70% similarity threshold
                        pair_key = tuple(sorted([name_i, name_j]))
                        if pair_key not in reported:
                            reported.add(pair_key)
                            snippet = lines[line_i - 1] if line_i <= len(lines) else ""
                            issues.append(Issue(
                                rule_id=self.id,
                                rule_name=self.name,
                                severity=self.severity,
                                message=(
                                    f"Functions '{name_i}' and '{name_j}' are structurally similar "
                                    f"({similarity:.0%} similarity). Consider merging or parameterizing."
                                ),
                                file_path=file_path,
                                line=line_i,
                                code_snippet=snippet.strip(),
                                suggestion="Consider merging these functions with a parameter to handle differences.",
                                category=self.category,
                                language="python",
                            ))

        return issues

    def _get_signature_structure(self, node: ast.AST) -> str:
        """Extract the structural signature of a function.

        Captures the number of arguments, their types (positional, keyword, etc.),
        and the return type structure.

        Args:
            node: Function AST node.

        Returns:
            Structural signature string.
        """
        parts = []
        parts.append(f"args={len(node.args.args)}")
        parts.append(f"defaults={len(node.args.defaults)}")
        parts.append(f"kwonly={len(node.args.kwonlyargs)}")
        parts.append(f"vararg={node.args.vararg is not None}")
        parts.append(f"kwarg={node.args.kwarg is not None}")
        return "|".join(parts)

    def _normalize_for_similarity(self, code: str) -> str:
        """Normalize code for structural similarity comparison.

        Args:
            code: Source code string.

        Returns:
            Normalized code string.
        """
        # Remove comments
        code = re.sub(r"#.*$", "", code, flags=re.MULTILINE)
        # Remove docstrings
        code = re.sub(r'"""[\s\S]*?"""', "", code)
        code = re.sub(r"'''[\s\S]*?'''", "", code)
        # Remove string literals
        code = re.sub(r'"[^"]*"', '""', code)
        code = re.sub(r"'[^']*'", "''", code)
        # Remove numbers
        code = re.sub(r"\b\d+\.?\d*\b", "0", code)
        # Remove variable names (simple heuristic)
        code = re.sub(r"\b[a-z_]\w*\b", "VAR", code)
        # Normalize whitespace
        code = re.sub(r"\s+", " ", code).strip()
        return code

    def _compute_similarity(self, text1: str, text2: str) -> float:
        """Compute similarity ratio between two strings.

        Uses a simple token-level comparison.

        Args:
            text1: First text string.
            text2: Second text string.

        Returns:
            Similarity ratio between 0.0 and 1.0.
        """
        tokens1 = text1.split()
        tokens2 = text2.split()

        if not tokens1 or not tokens2:
            return 0.0

        # Use set-based Jaccard similarity
        set1 = set(tokens1)
        set2 = set(tokens2)

        intersection = set1 & set2
        union = set1 | set2

        if not union:
            return 1.0

        return len(intersection) / len(union)
