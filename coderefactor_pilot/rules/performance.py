"""
Performance issue detection rules.

Detects common performance anti-patterns including string concatenation in loops,
unnecessary list copies, global variable lookups, and other performance concerns.
"""

import ast
import re
from typing import List

from coderefactor_pilot.rules.base import BaseRule, Issue, Severity


class StringConcatenationInLoopRule(BaseRule):
    """Detects string concatenation inside loops.

    String concatenation using + in a loop creates many intermediate
    string objects. Use list comprehension with join() or StringBuilder
    pattern instead.
    """

    id = "PERF001"
    name = "String Concatenation in Loop"
    description = "Avoid string concatenation in loops. Use join() or list comprehension instead."
    severity = Severity.MEDIUM
    category = "performance"
    languages = ["python", "javascript", "typescript", "go"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for string concatenation in loops.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        if language == "python":
            return self._check_python(content, file_path)
        else:
            return self._check_generic(content, file_path, language)

    def _check_python(self, content: str, file_path: str) -> List[Issue]:
        """Check Python code for string concatenation in loops using AST.

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
            if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
                # Look for augmented assign (+=) with strings inside the loop
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign):
                        if isinstance(child.op, ast.Add):
                            # Check if the target is likely a string
                            if isinstance(child.target, ast.Name):
                                issues.append(Issue(
                                    rule_id=self.id,
                                    rule_name=self.name,
                                    severity=self.severity,
                                    message=(
                                        f"String concatenation with '+=' detected inside a loop "
                                        f"on variable '{child.target.id}'. Use a list and join() instead."
                                    ),
                                    file_path=file_path,
                                    line=child.lineno,
                                    code_snippet=lines[child.lineno - 1].strip() if child.lineno <= len(lines) else "",
                                    suggestion=(
                                        f"Build a list and use ''.join(list) instead of "
                                        f"concatenating with '+=' in a loop."
                                    ),
                                    category=self.category,
                                    language="python",
                                ))

                    elif isinstance(child, ast.BinOp):
                        if isinstance(child.op, ast.Add):
                            # Check if either side is a string constant
                            if isinstance(child.left, ast.Constant) and isinstance(child.left.value, str):
                                issues.append(Issue(
                                    rule_id=self.id,
                                    rule_name=self.name,
                                    severity=self.severity,
                                    message=(
                                        "String concatenation detected inside a loop. "
                                        "Consider using join() or f-strings."
                                    ),
                                    file_path=file_path,
                                    line=child.lineno,
                                    code_snippet=lines[child.lineno - 1].strip() if child.lineno <= len(lines) else "",
                                    suggestion="Use ''.join() or f-strings for string building.",
                                    category=self.category,
                                    language="python",
                                ))

        return issues

    def _check_generic(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check non-Python code for string concatenation in loops.

        Args:
            content: Source code content.
            file_path: Path to the file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()

        # Track if we're inside a loop
        in_loop = False
        loop_indent = -1

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("*"):
                continue

            indent = len(line) - len(line.lstrip())

            # Detect loop start
            if re.match(r"\s*(for|while)\s*\(", stripped) or re.match(r"\s*for\s+\w+\s+in\s+", stripped):
                in_loop = True
                loop_indent = indent
                continue

            # Detect loop end (for brace-based languages)
            if in_loop and stripped == "}" and indent <= loop_indent:
                in_loop = False
                continue

            # Check for string concatenation inside loop
            if in_loop and "+=" in stripped and ("'" in stripped or '"' in stripped):
                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message="String concatenation with '+=' detected inside a loop. Use array join() instead.",
                    file_path=file_path,
                    line=i + 1,
                    code_snippet=stripped[:100],
                    suggestion="Build an array and use array.join('') instead of string concatenation in loops.",
                    category=self.category,
                    language=language,
                ))

        return issues


class UnnecessaryListCopyRule(BaseRule):
    """Detects unnecessary list/dict copies.

    Making unnecessary copies of large data structures wastes memory
    and CPU time.
    """

    id = "PERF002"
    name = "Unnecessary List/Dict Copy"
    description = "Detects unnecessary copying of lists or dictionaries."
    severity = Severity.LOW
    category = "performance"
    languages = ["python"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check Python code for unnecessary list/dict copies.

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
            if isinstance(node, ast.Call):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name in ("list", "dict", "set", "tuple"):
                    # Check if the argument is already the correct type
                    if node.args:
                        arg = node.args[0]
                        if isinstance(arg, ast.Name):
                            # list(x) where x is already a list is wasteful
                            line_num = node.lineno
                            snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                            issues.append(Issue(
                                rule_id=self.id,
                                rule_name=self.name,
                                severity=self.severity,
                                message=(
                                    f"Potentially unnecessary copy: {func_name}({arg.id}). "
                                    f"If '{arg.id}' is already a {func_name}, "
                                    f"this creates an unnecessary copy."
                                ),
                                file_path=file_path,
                                line=line_num,
                                code_snippet=snippet.strip(),
                                suggestion=(
                                    f"If you need a copy, use {arg.id}.copy() for clarity. "
                                    f"If you don't need a copy, use '{arg.id}' directly."
                                ),
                                category=self.category,
                                language="python",
                            ))

                elif func_name == "copy":
                    if isinstance(node.func, ast.Attribute):
                        line_num = node.lineno
                        snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                        issues.append(Issue(
                            rule_id=self.id,
                            rule_name=self.name,
                            severity=self.severity,
                            message=f"List/dict copy detected. Verify this copy is necessary.",
                            file_path=file_path,
                            line=line_num,
                            code_snippet=snippet.strip(),
                            suggestion="If the original data is not modified elsewhere, this copy may be unnecessary.",
                            category=self.category,
                            language="python",
                        ))

        return issues


class GlobalVariableLookupRule(BaseRule):
    """Detects repeated global variable lookups inside functions.

    Accessing global variables inside tight loops is slower than
    local variable access. Caching global references as locals
    can improve performance.
    """

    id = "PERF003"
    name = "Global Variable Lookup in Loop"
    description = "Cache global variable references as local variables for better performance."
    severity = Severity.LOW
    category = "performance"
    languages = ["python"]

    # Common global names that are frequently looked up
    COMMON_GLOBALS = {"len", "range", "str", "int", "float", "list", "dict", "set",
                      "print", "enumerate", "zip", "map", "filter", "sorted", "reversed",
                      "isinstance", "type", "hasattr", "getattr", "setattr"}

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check Python code for repeated global lookups in loops.

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
            if isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
                # Find all Name references inside the loop body
                name_refs: dict = {}
                for child in ast.walk(node):
                    if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                        name = child.id
                        if name in self.COMMON_GLOBALS:
                            name_refs[name] = name_refs.get(name, 0) + 1

                # Report if a global is referenced multiple times in a loop
                for name, count in name_refs.items():
                    if count >= 3:
                        line_num = node.lineno
                        snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                        issues.append(Issue(
                            rule_id=self.id,
                            rule_name=self.name,
                            severity=self.severity,
                            message=(
                                f"Built-in '{name}' is referenced {count} times inside a loop. "
                                f"Consider caching it as a local variable: '_{name} = {name}'."
                            ),
                            file_path=file_path,
                            line=line_num,
                            code_snippet=snippet.strip(),
                            suggestion=f"Add '_{name} = {name}' before the loop for faster lookups.",
                            category=self.category,
                            language="python",
                        ))

        return issues


class InefficientDataTypeRule(BaseRule):
    """Detects inefficient data type usage.

    Checks for using lists when sets would be more efficient for
    membership testing, and other data type anti-patterns.
    """

    id = "PERF004"
    name = "Inefficient Data Type"
    description = "Use appropriate data types for better performance (e.g., sets for membership tests)."
    severity = Severity.LOW
    category = "performance"
    languages = ["python"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check Python code for inefficient data type usage.

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
            # Check for 'in' operator with list
            if isinstance(node, ast.Compare):
                for op, comparator in zip(node.ops, node.comparators):
                    if isinstance(op, ast.In):
                        # Check if the comparator is a list literal
                        if isinstance(comparator, ast.List):
                            if len(comparator.elts) > 3:
                                line_num = node.lineno
                                snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                                issues.append(Issue(
                                    rule_id=self.id,
                                    rule_name=self.name,
                                    severity=self.severity,
                                    message=(
                                        f"Membership test 'in' on a list with {len(comparator.elts)} elements. "
                                        f"Use a set for O(1) lookups instead of O(n) list lookups."
                                    ),
                                    file_path=file_path,
                                    line=line_num,
                                    code_snippet=snippet.strip(),
                                    suggestion="Convert the list to a set for faster membership testing.",
                                    category=self.category,
                                    language="python",
                                ))

        return issues


class LazyImportRule(BaseRule):
    """Detects heavy imports at module level that could be lazily imported.

    Some modules are expensive to import and should be imported inside
    functions when they are actually needed.
    """

    id = "PERF005"
    name = "Heavy Module Import"
    description = "Consider lazy-importing heavy modules to improve startup time."
    severity = Severity.LOW
    category = "performance"
    languages = ["python"]

    # Modules that are typically heavy
    HEAVY_MODULES = {
        "pandas", "numpy", "matplotlib", "scipy", "sklearn",
        "tensorflow", "torch", "cv2", "PIL", "django",
        "flask", "sqlalchemy", "requests", "boto3",
    }

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check Python code for heavy module-level imports.

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

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split(".")[0]
                    if module_name in self.HEAVY_MODULES:
                        line_num = node.lineno
                        snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                        issues.append(Issue(
                            rule_id=self.id,
                            rule_name=self.name,
                            severity=self.severity,
                            message=(
                                f"Heavy module '{alias.name}' imported at module level. "
                                f"Consider lazy-importing inside the function that uses it."
                            ),
                            file_path=file_path,
                            line=line_num,
                            code_snippet=snippet.strip(),
                            suggestion=f"Move 'import {alias.name}' inside the function that uses it.",
                            category=self.category,
                            language="python",
                        ))

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split(".")[0]
                    if module_name in self.HEAVY_MODULES:
                        line_num = node.lineno
                        snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                        issues.append(Issue(
                            rule_id=self.id,
                            rule_name=self.name,
                            severity=self.severity,
                            message=(
                                f"Heavy module '{node.module}' imported at module level. "
                                f"Consider lazy-importing inside the function that uses it."
                            ),
                            file_path=file_path,
                            line=line_num,
                            code_snippet=snippet.strip(),
                            suggestion=f"Move 'from {node.module} import ...' inside the function that uses it.",
                            category=self.category,
                            language="python",
                        ))

        return issues


class UnusedImportRule(BaseRule):
    """Detects unused imports in Python files.

    Unused imports add unnecessary startup time and clutter the namespace.
    """

    id = "PERF006"
    name = "Unused Import"
    description = "Remove unused imports to improve startup time and reduce namespace clutter."
    severity = Severity.LOW
    category = "performance"
    languages = ["python"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check Python code for unused imports.

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

        # Collect all imports
        imports: dict = {}  # name -> (line_number, import_statement)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name.split(".")[0]
                    imports[name] = (node.lineno, f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        continue  # Skip star imports
                    name = alias.asname or alias.name
                    imports[name] = (node.lineno, f"from {node.module} import {alias.name}")

        # Collect all name usages in the file (excluding import statements)
        used_names: set = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

        # Find unused imports
        for name, (line_num, import_stmt) in imports.items():
            if name not in used_names:
                # Skip common patterns like __all__
                if name.startswith("__") and name.endswith("__"):
                    continue
                snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message=f"Unused import: '{import_stmt}'. Remove it to improve startup time.",
                    file_path=file_path,
                    line=line_num,
                    code_snippet=snippet.strip(),
                    suggestion=f"Remove the unused import: {import_stmt}",
                    category=self.category,
                    language="python",
                ))

        return issues
