"""
Code style detection rules.

Checks for style issues like line length, function length, file length,
parameter count, trailing whitespace, and other formatting concerns.
"""

import ast
import re
from typing import List

from coderefactor_pilot.rules.base import BaseRule, Issue, Severity


class LineLengthRule(BaseRule):
    """Detects lines that exceed the maximum allowed length.

    Long lines reduce readability, especially in diff views and
    narrow terminal windows.

    Maximum line length is configurable via 'max_line_length' (default: 120).
    """

    id = "STY001"
    name = "Line Too Long"
    description = "Lines should not exceed the maximum allowed length."
    severity = Severity.LOW
    category = "style"
    languages = ["python", "javascript", "typescript", "go"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for lines that exceed the maximum length.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []
        max_length = self.get_config("max_line_length", 120)
        lines = content.splitlines()

        for i, line in enumerate(lines):
            if len(line) > max_length:
                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message=(
                        f"Line is {len(line)} characters long (max: {max_length}). "
                        f"Consider breaking it into multiple lines."
                    ),
                    file_path=file_path,
                    line=i + 1,
                    code_snippet=line[:80] + "...",
                    suggestion=f"Break the line to be at most {max_length} characters.",
                    category=self.category,
                    language=language,
                ))

        return issues


class FunctionLengthRule(BaseRule):
    """Detects functions that are too long.

    Long functions are harder to understand, test, and maintain.
    They often contain multiple levels of abstraction and should
    be broken down into smaller, focused functions.

    Maximum function length is configurable via 'max_function_length' (default: 50).
    """

    id = "STY002"
    name = "Function Too Long"
    description = "Functions should not exceed the maximum allowed number of lines."
    severity = Severity.MEDIUM
    category = "style"
    languages = ["python", "javascript", "typescript", "go"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for functions that exceed the maximum length.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        max_length = self.get_config("max_function_length", 50)

        if language == "python":
            return self._check_python(content, file_path, max_length)
        else:
            return self._check_generic(content, file_path, language, max_length)

    def _check_python(self, content: str, file_path: str, max_length: int) -> List[Issue]:
        """Check Python code for long functions using AST.

        Args:
            content: Python source code.
            file_path: Path to the file.
            max_length: Maximum allowed function length.

        Returns:
            List of issues found.
        """
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues

        lines = content.splitlines()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = node.lineno
                end = node.end_lineno or start
                func_length = end - start + 1

                if func_length > max_length:
                    snippet = lines[start - 1] if start <= len(lines) else ""
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=Severity.HIGH if func_length > max_length * 2 else Severity.MEDIUM,
                        message=(
                            f"Function '{node.name}' is {func_length} lines long "
                            f"(max: {max_length}). Consider breaking it into smaller functions."
                        ),
                        file_path=file_path,
                        line=start,
                        end_line=end,
                        code_snippet=snippet.strip(),
                        suggestion=f"Break '{node.name}' into smaller, focused functions (target: <= {max_length} lines).",
                        category=self.category,
                        language="python",
                    ))

        return issues

    def _check_generic(self, content: str, file_path: str, language: str,
                       max_length: int) -> List[Issue]:
        """Check non-Python code for long functions using brace matching.

        Args:
            content: Source code content.
            file_path: Path to the file.
            language: Programming language.
            max_length: Maximum allowed function length.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()

        # Find function definitions
        func_pattern = re.compile(
            r"^\s*(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>)"
            r"|func\s+(?:\([^)]*\)\s+)?(\w+))"
        )

        for match in func_pattern.finditer(content):
            func_name = next(g for g in match.groups() if g is not None)
            start_line = content[:match.start()].count("\n") + 1

            # Find function end by brace matching
            brace_count = 0
            func_end = match.end()
            in_function = False

            for i in range(match.end(), len(content)):
                if content[i] == "{":
                    brace_count += 1
                    in_function = True
                elif content[i] == "}":
                    brace_count -= 1
                    if in_function and brace_count == 0:
                        func_end = i
                        break

            end_line = content[:func_end].count("\n") + 1
            func_length = end_line - start_line + 1

            if func_length > max_length:
                snippet = lines[start_line - 1] if start_line <= len(lines) else ""
                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=Severity.HIGH if func_length > max_length * 2 else Severity.MEDIUM,
                    message=(
                        f"Function '{func_name}' is {func_length} lines long "
                        f"(max: {max_length}). Consider breaking it into smaller functions."
                    ),
                    file_path=file_path,
                    line=start_line,
                    end_line=end_line,
                    code_snippet=snippet.strip(),
                    suggestion=f"Break '{func_name}' into smaller functions (target: <= {max_length} lines).",
                    category=self.category,
                    language=language,
                ))

        return issues


class FileLengthRule(BaseRule):
    """Detects files that are too long.

    Very long files are harder to navigate and maintain.
    Consider splitting into multiple modules.

    Maximum file length is configurable via 'max_file_length' (default: 500).
    """

    id = "STY003"
    name = "File Too Long"
    description = "Source files should not exceed the maximum allowed number of lines."
    severity = Severity.MEDIUM
    category = "style"
    languages = ["python", "javascript", "typescript", "go"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check if a file exceeds the maximum length.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []
        max_length = self.get_config("max_file_length", 500)
        line_count = len(content.splitlines())

        if line_count > max_length:
            issues.append(Issue(
                rule_id=self.id,
                rule_name=self.name,
                severity=Severity.HIGH if line_count > max_length * 2 else Severity.MEDIUM,
                message=(
                    f"File has {line_count} lines (max: {max_length}). "
                    f"Consider splitting into multiple modules."
                ),
                file_path=file_path,
                line=1,
                suggestion=f"Split this file into smaller modules (target: <= {max_length} lines).",
                category=self.category,
                language=language,
            ))

        return issues


class TooManyParametersRule(BaseRule):
    """Detects functions with too many parameters.

    Functions with many parameters are hard to call correctly and
    suggest the function is doing too much. Consider using parameter
    objects or builder patterns.

    Maximum parameters is configurable via 'max_parameters' (default: 7).
    """

    id = "STY004"
    name = "Too Many Parameters"
    description = "Functions should not have too many parameters."
    severity = Severity.MEDIUM
    category = "style"
    languages = ["python", "javascript", "typescript", "go"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for functions with too many parameters.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        max_params = self.get_config("max_parameters", 7)

        if language == "python":
            return self._check_python(content, file_path, max_params)
        else:
            return self._check_generic(content, file_path, language, max_params)

    def _check_python(self, content: str, file_path: str, max_params: int) -> List[Issue]:
        """Check Python code for functions with too many parameters.

        Args:
            content: Python source code.
            file_path: Path to the file.
            max_params: Maximum allowed parameters.

        Returns:
            List of issues found.
        """
        issues = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues

        lines = content.splitlines()

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Count regular args (excluding self/cls)
                param_count = len(node.args.args)
                if node.args.args and node.args.args[0].arg in ("self", "cls"):
                    param_count -= 1

                # Add keyword-only args
                param_count += len(node.args.kwonlyargs)

                # Add *args and **kwargs
                if node.args.vararg:
                    param_count += 1
                if node.args.kwarg:
                    param_count += 1

                if param_count > max_params:
                    line_num = node.lineno
                    snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=(
                            f"Function '{node.name}' has {param_count} parameters "
                            f"(max: {max_params}). Consider using a parameter object."
                        ),
                        file_path=file_path,
                        line=line_num,
                        code_snippet=snippet.strip(),
                        suggestion="Consider grouping related parameters into a dataclass or dict.",
                        category=self.category,
                        language="python",
                    ))

        return issues

    def _check_generic(self, content: str, file_path: str, language: str,
                       max_params: int) -> List[Issue]:
        """Check non-Python code for functions with too many parameters.

        Args:
            content: Source code content.
            file_path: Path to the file.
            language: Programming language.
            max_params: Maximum allowed parameters.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()

        # Pattern for function definitions with parameters
        func_pattern = re.compile(
            r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?"
            r"(?:function|\(([^)]*)\)\s*=>)|func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(([^)]*)\))"
        )

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue

            match = func_pattern.search(stripped)
            if not match:
                continue

            func_name = next(g for g in match.groups() if g is not None and "(" not in g)

            # Find the parameter list
            paren_match = re.search(r"\(([^)]*)\)", stripped)
            if not paren_match:
                continue

            params_str = paren_match.group(1).strip()
            if not params_str:
                continue

            # Count parameters
            params = [p.strip() for p in params_str.split(",") if p.strip()]
            # Filter out type annotations in TypeScript
            if language == "typescript":
                params = [p.split(":")[0].strip() for p in params]

            param_count = len(params)

            if param_count > max_params:
                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message=(
                        f"Function '{func_name}' has {param_count} parameters "
                        f"(max: {max_params}). Consider using a parameter object."
                    ),
                    file_path=file_path,
                    line=i + 1,
                    code_snippet=stripped[:100],
                    suggestion="Consider grouping related parameters into an options object.",
                    category=self.category,
                    language=language,
                ))

        return issues


class TrailingWhitespaceRule(BaseRule):
    """Detects trailing whitespace on lines.

    Trailing whitespace is a common style issue that creates
    unnecessary diffs.
    """

    id = "STY005"
    name = "Trailing Whitespace"
    description = "Lines should not have trailing whitespace."
    severity = Severity.LOW
    category = "style"
    languages = ["python", "javascript", "typescript", "go"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for trailing whitespace.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()

        for i, line in enumerate(lines):
            if line != line.rstrip():
                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message="Trailing whitespace detected.",
                    file_path=file_path,
                    line=i + 1,
                    code_snippet=line.rstrip() + " <-- trailing whitespace",
                    suggestion="Remove trailing whitespace.",
                    category=self.category,
                    language=language,
                ))

        return issues


class MissingDocstringRule(BaseRule):
    """Detects public functions and classes without docstrings.

    All public functions and classes should have docstrings
    explaining their purpose, parameters, and return values.
    """

    id = "STY006"
    name = "Missing Docstring"
    description = "Public functions and classes should have docstrings."
    severity = Severity.LOW
    category = "style"
    languages = ["python"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check Python code for missing docstrings.

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

        for node in ast.walk(tree):
            # Skip private/dunder methods
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue

                if not self._has_docstring(node):
                    line_num = node.lineno
                    snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=f"Public function '{node.name}' is missing a docstring.",
                        file_path=file_path,
                        line=line_num,
                        code_snippet=snippet.strip(),
                        suggestion="Add a docstring explaining the function's purpose, parameters, and return value.",
                        category=self.category,
                        language="python",
                    ))

            elif isinstance(node, ast.ClassDef):
                if node.name.startswith("_"):
                    continue

                if not self._has_docstring(node):
                    line_num = node.lineno
                    snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=f"Public class '{node.name}' is missing a docstring.",
                        file_path=file_path,
                        line=line_num,
                        code_snippet=snippet.strip(),
                        suggestion="Add a docstring explaining the class's purpose and usage.",
                        category=self.category,
                        language="python",
                    ))

        return issues

    def _has_docstring(self, node: ast.AST) -> bool:
        """Check if an AST node has a docstring.

        Args:
            node: AST node to check.

        Returns:
            True if the node has a docstring.
        """
        if not (node.body and isinstance(node.body[0], ast.Expr)):
            return False

        expr_value = node.body[0].value
        if isinstance(expr_value, ast.Constant) and isinstance(expr_value.value, str):
            return True

        # Python 3.7 compatibility
        if isinstance(expr_value, ast.Str):
            return True

        return False
