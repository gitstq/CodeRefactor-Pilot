"""
Naming convention detection rules.

Checks identifiers for compliance with language-specific naming conventions
including PEP 8 for Python, camelCase for JavaScript/TypeScript, and
camelCase/PascalCase for Go.
"""

import ast
import re
import keyword
from typing import List

from coderefactor_pilot.rules.base import BaseRule, Issue, Severity


class SnakeCaseNamingRule(BaseRule):
    """Checks that Python identifiers follow snake_case naming convention.

    Applies to function names, variable names, and method names.
    Class names should follow PascalCase (checked separately).
    """

    id = "NM001"
    name = "Snake Case Naming (Python)"
    description = "Python function and variable names should follow snake_case convention (PEP 8)."
    severity = Severity.LOW
    category = "naming"
    languages = ["python"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check Python code for snake_case naming violations.

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
            # Check function names
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not self._is_snake_case(node.name) and not node.name.startswith("_"):
                    line_num = node.lineno
                    snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=(
                            f"Function '{node.name}' should use snake_case naming. "
                            f"Suggested: '{self._to_snake_case(node.name)}'"
                        ),
                        file_path=file_path,
                        line=line_num,
                        code_snippet=snippet.strip(),
                        suggestion=f"Rename to '{self._to_snake_case(node.name)}'",
                        category=self.category,
                        language="python",
                    ))

            # Check variable names in assignments
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        if (not self._is_snake_case(name)
                                and not name.startswith("_")
                                and not name.isupper()  # Allow UPPER_CASE constants
                                and not keyword.iskeyword(name)):
                            line_num = node.lineno
                            snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                            issues.append(Issue(
                                rule_id=self.id,
                                rule_name=self.name,
                                severity=self.severity,
                                message=(
                                    f"Variable '{name}' should use snake_case naming. "
                                    f"Suggested: '{self._to_snake_case(name)}'"
                                ),
                                file_path=file_path,
                                line=line_num,
                                code_snippet=snippet.strip(),
                                suggestion=f"Rename to '{self._to_snake_case(name)}'",
                                category=self.category,
                                language="python",
                            ))

            # Check function argument names
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for arg in node.args.args:
                    if (arg.arg != "self" and arg.arg != "cls"
                            and not self._is_snake_case(arg.arg)
                            and not arg.arg.startswith("_")):
                        line_num = node.lineno
                        snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                        issues.append(Issue(
                            rule_id=self.id,
                            rule_name=self.name,
                            severity=self.severity,
                            message=(
                                f"Parameter '{arg.arg}' should use snake_case naming. "
                                f"Suggested: '{self._to_snake_case(arg.arg)}'"
                            ),
                            file_path=file_path,
                            line=line_num,
                            code_snippet=snippet.strip(),
                            suggestion=f"Rename to '{self._to_snake_case(arg.arg)}'",
                            category=self.category,
                            language="python",
                        ))

        return issues

    def _is_snake_case(self, name: str) -> bool:
        """Check if a name follows snake_case convention.

        Allows leading underscores and single-word lowercase names.

        Args:
            name: Identifier name to check.

        Returns:
            True if the name follows snake_case.
        """
        # Strip leading underscores
        stripped = name.lstrip("_")
        if not stripped:
            return True

        # Must start with lowercase letter
        if not stripped[0].islower():
            return False

        # Should only contain lowercase letters, digits, and underscores
        return bool(re.match(r"^[a-z][a-z0-9_]*$", stripped))

    def _to_snake_case(self, name: str) -> str:
        """Convert a name to snake_case.

        Args:
            name: Identifier name to convert.

        Returns:
            snake_case version of the name.
        """
        # Handle camelCase and PascalCase
        s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
        s2 = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s1)
        return s2.lower().replace("-", "_")


class PascalCaseClassRule(BaseRule):
    """Checks that Python class names follow PascalCase naming convention.

    Class names should use PascalCase (also known as CapWords) per PEP 8.
    """

    id = "NM002"
    name = "PascalCase Class Names (Python)"
    description = "Python class names should follow PascalCase convention (PEP 8)."
    severity = Severity.LOW
    category = "naming"
    languages = ["python"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check Python code for PascalCase class naming violations.

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
            if isinstance(node, ast.ClassDef):
                if not self._is_pascal_case(node.name):
                    line_num = node.lineno
                    snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=(
                            f"Class '{node.name}' should use PascalCase naming. "
                            f"Suggested: '{self._to_pascal_case(node.name)}'"
                        ),
                        file_path=file_path,
                        line=line_num,
                        code_snippet=snippet.strip(),
                        suggestion=f"Rename to '{self._to_pascal_case(node.name)}'",
                        category=self.category,
                        language="python",
                    ))

        return issues

    def _is_pascal_case(self, name: str) -> bool:
        """Check if a name follows PascalCase convention.

        Args:
            name: Class name to check.

        Returns:
            True if the name follows PascalCase.
        """
        if not name:
            return False
        return bool(re.match(r"^[A-Z][a-zA-Z0-9]*$", name))

    def _to_pascal_case(self, name: str) -> str:
        """Convert a name to PascalCase.

        Args:
            name: Identifier name to convert.

        Returns:
            PascalCase version of the name.
        """
        # Split on underscores and hyphens, capitalize each part
        parts = re.split(r"[_\-\s]+", name)
        return "".join(part.capitalize() for part in parts if part)


class CamelCaseNamingRule(BaseRule):
    """Checks that JavaScript/TypeScript identifiers follow camelCase convention.

    Applies to function names, variable names, and method names.
    Class names should follow PascalCase.
    """

    id = "NM003"
    name = "camelCase Naming (JS/TS)"
    description = "JavaScript/TypeScript functions and variables should use camelCase naming."
    severity = Severity.LOW
    category = "naming"
    languages = ["javascript", "typescript"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check JS/TS code for camelCase naming violations.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        if language not in ("javascript", "typescript"):
            return []

        issues = []
        lines = content.splitlines()

        # Pattern for function declarations and variable assignments
        func_decl = re.compile(
            r"(?:function\s+)([A-Za-z_$][\w$]*)"
        )
        const_decl = re.compile(
            r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*="
        )
        arrow_func = re.compile(
            r"(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[\w$]+)\s*=>"
        )

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("*"):
                continue

            # Check function declarations
            for match in func_decl.finditer(stripped):
                name = match.group(1)
                if (not self._is_camel_case(name)
                        and not name.startswith("_")
                        and not self._is_pascal_case(name)):
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=f"Function '{name}' should use camelCase naming.",
                        file_path=file_path,
                        line=i + 1,
                        code_snippet=stripped,
                        suggestion=f"Rename to '{self._to_camel_case(name)}'",
                        category=self.category,
                        language=language,
                    ))

            # Check variable declarations
            for match in const_decl.finditer(stripped):
                name = match.group(1)
                if (not self._is_camel_case(name)
                        and not name.startswith("_")
                        and not name.isupper()
                        and not self._is_pascal_case(name)):
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=f"Variable '{name}' should use camelCase naming.",
                        file_path=file_path,
                        line=i + 1,
                        code_snippet=stripped,
                        suggestion=f"Rename to '{self._to_camel_case(name)}'",
                        category=self.category,
                        language=language,
                    ))

        return issues

    def _is_camel_case(self, name: str) -> bool:
        """Check if a name follows camelCase convention.

        Args:
            name: Identifier name to check.

        Returns:
            True if the name follows camelCase.
        """
        if not name:
            return False
        return bool(re.match(r"^[a-z_$][a-zA-Z0-9_$]*$", name))

    def _is_pascal_case(self, name: str) -> bool:
        """Check if a name follows PascalCase convention.

        Args:
            name: Identifier name to check.

        Returns:
            True if the name follows PascalCase.
        """
        if not name:
            return False
        return bool(re.match(r"^[A-Z][a-zA-Z0-9_$]*$", name))

    def _to_camel_case(self, name: str) -> str:
        """Convert a name to camelCase.

        Args:
            name: Identifier name to convert.

        Returns:
            camelCase version of the name.
        """
        parts = re.split(r"[_\-\s]+", name)
        if not parts:
            return name
        return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])


class GoNamingRule(BaseRule):
    """Checks Go code naming conventions.

    Go uses camelCase for unexported and PascalCase for exported identifiers.
    """

    id = "NM004"
    name = "Go Naming Convention"
    description = "Go identifiers should follow standard Go naming conventions."
    severity = Severity.LOW
    category = "naming"
    languages = ["go"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check Go code for naming convention violations.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        if language != "go":
            return []

        issues = []
        lines = content.splitlines()

        # Pattern for function declarations
        func_pattern = re.compile(r"func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(")
        # Pattern for variable declarations
        var_pattern = re.compile(r"(?:var|:=)\s*(\w+)")
        # Pattern for type declarations
        type_pattern = re.compile(r"type\s+(\w+)\s+(?:struct|interface)")

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue

            # Check function names
            for match in func_pattern.finditer(stripped):
                name = match.group(1)
                if name[0].isupper():
                    # Exported: should be PascalCase
                    if not re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
                        issues.append(Issue(
                            rule_id=self.id,
                            rule_name=self.name,
                            severity=self.severity,
                            message=f"Exported function '{name}' should use PascalCase.",
                            file_path=file_path,
                            line=i + 1,
                            code_snippet=stripped,
                            category=self.category,
                            language="go",
                        ))
                else:
                    # Unexported: should be camelCase
                    if not re.match(r"^[a-z][a-zA-Z0-9]*$", name):
                        issues.append(Issue(
                            rule_id=self.id,
                            rule_name=self.name,
                            severity=self.severity,
                            message=f"Unexported function '{name}' should use camelCase.",
                            file_path=file_path,
                            line=i + 1,
                            code_snippet=stripped,
                            category=self.category,
                            language="go",
                        ))

            # Check type names (should be PascalCase)
            for match in type_pattern.finditer(stripped):
                name = match.group(1)
                if not re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=f"Type '{name}' should use PascalCase.",
                        file_path=file_path,
                        line=i + 1,
                        code_snippet=stripped,
                        suggestion=f"Rename to '{name[0].upper() + name[1:]}'",
                        category=self.category,
                        language="go",
                    ))

        return issues


class ShortIdentifierRule(BaseRule):
    """Detects identifiers that are too short to be descriptive.

    Very short variable names (1-2 characters) can make code harder to understand
    except for loop counters and common idioms.
    """

    id = "NM005"
    name = "Short Identifier Names"
    description = "Identifiers should be descriptive and not too short (except loop counters)."
    severity = Severity.LOW
    category = "naming"
    languages = ["python", "javascript", "typescript", "go"]

    # Common short names that are acceptable
    ACCEPTABLE_SHORT_NAMES = {
        "i", "j", "k", "x", "y", "z",  # Loop counters
        "n", "m",  # Counters/numbers
        "e",  # Exception in except blocks
        "f",  # File handle (common idiom)
        "p",  # Pointers (C/Go idiom)
        "r",  # Reader/result
        "k", "v",  # Key-value in dict iteration
        "_",  # Discard variable
        "id", "ok", "fn", "db",  # Common abbreviations
    }

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for overly short identifier names.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []

        if language == "python":
            issues = self._check_python(content, file_path)
        else:
            issues = self._check_generic(content, file_path, language)

        return issues

    def _check_python(self, content: str, file_path: str) -> List[Issue]:
        """Check Python code for short identifiers.

        Args:
            content: Python source code.
            file_path: Path to the file.

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
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        if (len(name) <= 2
                                and name not in self.ACCEPTABLE_SHORT_NAMES
                                and not name.startswith("_")):
                            line_num = node.lineno
                            snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                            issues.append(Issue(
                                rule_id=self.id,
                                rule_name=self.name,
                                severity=self.severity,
                                message=f"Variable '{name}' is too short. Use a more descriptive name.",
                                file_path=file_path,
                                line=line_num,
                                code_snippet=snippet.strip(),
                                suggestion="Use a name that describes the variable's purpose.",
                                category=self.category,
                                language="python",
                            ))

        return issues

    def _check_generic(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check non-Python code for short identifiers.

        Args:
            content: Source code content.
            file_path: Path to the file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()

        # Pattern for variable declarations
        var_pattern = re.compile(
            r"(?:const|let|var|:=)\s*([A-Za-z_$][\w$]*)"
        )

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("*"):
                continue

            for match in var_pattern.finditer(stripped):
                name = match.group(1)
                if (len(name) <= 2
                        and name not in self.ACCEPTABLE_SHORT_NAMES
                        and not name.startswith("_")):
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=f"Variable '{name}' is too short. Use a more descriptive name.",
                        file_path=file_path,
                        line=i + 1,
                        code_snippet=stripped,
                        suggestion="Use a name that describes the variable's purpose.",
                        category=self.category,
                        language=language,
                    ))

        return issues
