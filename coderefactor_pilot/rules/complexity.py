"""
Complexity detection rules.

Detects cyclomatic complexity and cognitive complexity issues in code.
Uses AST-based analysis for Python and regex-based heuristics for other languages.
"""

import ast
import re
import keyword
from typing import Any, Dict, List, Optional

from coderefactor_pilot.rules.base import BaseRule, Issue, Severity


class CyclomaticComplexityRule(BaseRule):
    """Detects functions/methods with cyclomatic complexity above a threshold.

    Cyclomatic complexity counts the number of linearly independent paths
    through a function. Each decision point (if, for, while, try, and, or)
    increments the complexity by 1.

    Threshold is configurable via 'max_complexity' (default: 10).
    """

    id = "CC001"
    name = "Cyclomatic Complexity"
    description = "Functions/methods with high cyclomatic complexity are hard to test and maintain."
    severity = Severity.MEDIUM
    category = "complexity"
    languages = ["python", "javascript", "typescript", "go"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for cyclomatic complexity violations.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []
        max_complexity = self.get_config("max_complexity", 10)

        if language == "python":
            issues = self._check_python(content, file_path, max_complexity)
        else:
            issues = self._check_generic(content, file_path, language, max_complexity)

        return issues

    def _check_python(self, content: str, file_path: str, max_complexity: int) -> List[Issue]:
        """Check Python code using AST analysis.

        Args:
            content: Python source code.
            file_path: Path to the file.
            max_complexity: Maximum allowed complexity.

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
                complexity = self._compute_python_complexity(node)
                if complexity > max_complexity:
                    line_num = node.lineno
                    snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self._get_severity(complexity, max_complexity),
                        message=(
                            f"Function '{node.name}' has cyclomatic complexity of {complexity} "
                            f"(threshold: {max_complexity}). Consider breaking it into smaller functions."
                        ),
                        file_path=file_path,
                        line=line_num,
                        end_line=node.end_lineno,
                        code_snippet=snippet.strip(),
                        suggestion=(
                            f"Extract helper methods or use early returns to reduce complexity. "
                            f"Target: <= {max_complexity}."
                        ),
                        category=self.category,
                        language="python",
                    ))

        return issues

    def _compute_python_complexity(self, node: ast.AST) -> int:
        """Compute cyclomatic complexity of a Python function node.

        Args:
            node: AST node of the function.

        Returns:
            Cyclomatic complexity value.
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Each branching statement adds 1
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
                if child.ifs:
                    complexity += len(child.ifs)
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.IfExp):  # Ternary operator
                complexity += 1

        return complexity

    def _check_generic(self, content: str, file_path: str, language: str,
                       max_complexity: int) -> List[Issue]:
        """Check non-Python code using regex-based heuristics.

        Detects function definitions and counts branching statements within them.

        Args:
            content: Source code content.
            file_path: Path to the file.
            language: Programming language.
            max_complexity: Maximum allowed complexity.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()

        # Patterns for function definitions in different languages
        func_patterns = {
            "javascript": re.compile(
                r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))",
                re.MULTILINE
            ),
            "typescript": re.compile(
                r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))"
                r"|(?:async\s+)?(\w+)\s*\([^)]*\)\s*[:{]",
                re.MULTILINE
            ),
            "go": re.compile(
                r"func\s+(?:\([^)]*\)\s+)?(\w+)",
                re.MULTILINE
            ),
        }

        pattern = func_patterns.get(language)
        if not pattern:
            return issues

        # Find all function definitions with their positions
        functions = []
        for match in pattern.finditer(content):
            func_name = next(g for g in match.groups() if g is not None)
            start_pos = match.start()
            start_line = content[:start_pos].count("\n") + 1
            functions.append((func_name, start_line, start_pos))

        # For each function, estimate complexity until next function or EOF
        for i, (func_name, start_line, start_pos) in enumerate(functions):
            # Find the end of this function (start of next function or EOF)
            if i + 1 < len(functions):
                end_pos = functions[i + 1][2]
            else:
                end_pos = len(content)

            func_body = content[start_pos:end_pos]
            complexity = self._estimate_generic_complexity(func_body, language)

            if complexity > max_complexity:
                snippet = lines[start_line - 1] if start_line <= len(lines) else ""
                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self._get_severity(complexity, max_complexity),
                    message=(
                        f"Function '{func_name}' has estimated cyclomatic complexity of {complexity} "
                        f"(threshold: {max_complexity}). Consider refactoring."
                    ),
                    file_path=file_path,
                    line=start_line,
                    code_snippet=snippet.strip(),
                    suggestion="Extract helper functions to reduce complexity.",
                    category=self.category,
                    language=language,
                ))

        return issues

    def _estimate_generic_complexity(self, code: str, language: str) -> int:
        """Estimate cyclomatic complexity for non-Python code.

        Counts branching keywords in the function body.

        Args:
            code: Function body text.
            language: Programming language.

        Returns:
            Estimated cyclomatic complexity.
        """
        complexity = 1  # Base complexity

        # Common branching keywords across languages
        branching_keywords = [
            r"\bif\b", r"\belse\s+if\b", r"\belif\b", r"\bfor\b",
            r"\bwhile\b", r"\bcase\b", r"\bcatch\b", r"\bexcept\b",
            r"\?\?", r"\?\.",  # Null coalescing / optional chaining
        ]

        # Language-specific additions
        if language in ("javascript", "typescript"):
            branching_keywords.extend([
                r"\&\&", r"\|\|",  # Logical operators
                r"\?",  # Ternary operator (simplified)
            ])
        elif language == "go":
            branching_keywords.extend([
                r"\bselect\b", r"\bswitch\b", r"\bgoto\b",
            ])

        for kw in branching_keywords:
            complexity += len(re.findall(kw, code))

        return complexity

    def _get_severity(self, complexity: int, threshold: int) -> Severity:
        """Determine severity based on how much complexity exceeds threshold.

        Args:
            complexity: Actual complexity value.
            threshold: Maximum allowed complexity.

        Returns:
            Appropriate severity level.
        """
        ratio = complexity / max(threshold, 1)
        if ratio >= 3.0:
            return Severity.CRITICAL
        elif ratio >= 2.0:
            return Severity.HIGH
        elif ratio >= 1.0:
            return Severity.MEDIUM
        return Severity.LOW


class CognitiveComplexityRule(BaseRule):
    """Detects functions with high cognitive complexity.

    Cognitive complexity measures how hard code is to understand by
    accounting for nesting, breaks in linear flow, and mental model
    required. It penalizes nesting more heavily than cyclomatic complexity.

    Threshold is configurable via 'max_cognitive_complexity' (default: 15).
    """

    id = "CC002"
    name = "Cognitive Complexity"
    description = "Functions with high cognitive complexity are difficult to read and understand."
    severity = Severity.MEDIUM
    category = "complexity"
    languages = ["python", "javascript", "typescript", "go"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for cognitive complexity violations.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []
        max_complexity = self.get_config("max_cognitive_complexity", 15)

        if language == "python":
            issues = self._check_python(content, file_path, max_complexity)
        else:
            issues = self._check_generic(content, file_path, language, max_complexity)

        return issues

    def _check_python(self, content: str, file_path: str, max_complexity: int) -> List[Issue]:
        """Check Python code for cognitive complexity.

        Args:
            content: Python source code.
            file_path: Path to the file.
            max_complexity: Maximum allowed cognitive complexity.

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
                cog_complexity = self._compute_python_cognitive_complexity(node, 0)
                if cog_complexity > max_complexity:
                    line_num = node.lineno
                    snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self._get_severity(cog_complexity, max_complexity),
                        message=(
                            f"Function '{node.name}' has cognitive complexity of {cog_complexity} "
                            f"(threshold: {max_complexity}). Consider simplifying control flow."
                        ),
                        file_path=file_path,
                        line=line_num,
                        end_line=node.end_lineno,
                        code_snippet=snippet.strip(),
                        suggestion=(
                            "Reduce nesting, use early returns/continues, "
                            "and extract complex conditions into well-named functions."
                        ),
                        category=self.category,
                        language="python",
                    ))

        return issues

    def _compute_python_cognitive_complexity(self, node: ast.AST, nesting: int) -> int:
        """Compute cognitive complexity of a Python function.

        Cognitive complexity rules:
        - Increments for if/elif/else/for/while/except/try/with (nesting + 1)
        - Increments for break/continue/goto (+1)
        - Nesting increment for nested structures
        - No increment for else/finally (just nesting)

        Args:
            node: AST node of the function.
            nesting: Current nesting level.

        Returns:
            Cognitive complexity value.
        """
        complexity = 0

        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.If):
                complexity += nesting + 1
                complexity += self._compute_python_cognitive_complexity(child, nesting + 1)
            elif isinstance(child, (ast.For, ast.AsyncFor, ast.While)):
                complexity += nesting + 1
                complexity += self._compute_python_cognitive_complexity(child, nesting + 1)
            elif isinstance(child, ast.Try):
                complexity += nesting + 1
                complexity += self._compute_python_cognitive_complexity(child, nesting + 1)
            elif isinstance(child, ast.With):
                complexity += nesting + 1
                complexity += self._compute_python_cognitive_complexity(child, nesting + 1)
            elif isinstance(child, ast.ExceptHandler):
                complexity += nesting + 1
                complexity += self._compute_python_cognitive_complexity(child, nesting)
            elif isinstance(child, ast.BoolOp):
                # and/or add nesting + 1 for each additional operand
                ops = len(child.values) - 1
                complexity += ops * (nesting + 1)
            elif isinstance(child, ast.IfExp):  # Ternary
                complexity += nesting + 1
            elif isinstance(child, (ast.Break, ast.Continue)):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += nesting + 1

        return complexity

    def _check_generic(self, content: str, file_path: str, language: str,
                       max_complexity: int) -> List[Issue]:
        """Check non-Python code for cognitive complexity.

        Uses indentation-based nesting estimation and keyword counting.

        Args:
            content: Source code content.
            file_path: Path to the file.
            language: Programming language.
            max_complexity: Maximum allowed cognitive complexity.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()

        # Find function boundaries
        func_pattern = re.compile(
            r"^\s*(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>)"
            r"|func\s+(?:\([^)]*\)\s+)?(\w+))",
            re.MULTILINE
        )

        for match in func_pattern.finditer(content):
            func_name = next(g for g in match.groups() if g is not None)
            start_line = content[:match.start()].count("\n") + 1

            # Find function end by tracking braces
            func_start = match.end()
            brace_count = 0
            func_end = func_start
            in_function = False

            for i in range(func_start, len(content)):
                if content[i] == "{":
                    brace_count += 1
                    in_function = True
                elif content[i] == "}":
                    brace_count -= 1
                    if in_function and brace_count == 0:
                        func_end = i
                        break

            func_body = content[func_start:func_end]
            cog_complexity = self._estimate_generic_cognitive_complexity(func_body, language)

            if cog_complexity > max_complexity:
                snippet = lines[start_line - 1] if start_line <= len(lines) else ""
                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self._get_severity(cog_complexity, max_complexity),
                    message=(
                        f"Function '{func_name}' has estimated cognitive complexity of "
                        f"{cog_complexity} (threshold: {max_complexity})."
                    ),
                    file_path=file_path,
                    line=start_line,
                    code_snippet=snippet.strip(),
                    suggestion="Reduce nesting and simplify control flow.",
                    category=self.category,
                    language=language,
                ))

        return issues

    def _estimate_generic_cognitive_complexity(self, code: str, language: str) -> int:
        """Estimate cognitive complexity for non-Python code.

        Uses indentation-based nesting estimation.

        Args:
            code: Function body text.
            language: Programming language.

        Returns:
            Estimated cognitive complexity.
        """
        complexity = 0
        lines = code.splitlines()

        # Keywords that increase complexity (with nesting penalty)
        structural_keywords = [
            r"\bif\b", r"\belse\s+if\b", r"\bfor\b", r"\bwhile\b",
            r"\bcatch\b", r"\bswitch\b", r"\bcase\b",
        ]

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("*"):
                continue

            # Estimate nesting from indentation
            indent = len(line) - len(line.lstrip())
            nesting = indent // 4  # Assume 4-space indent

            for kw in structural_keywords:
                if re.search(kw, stripped):
                    complexity += nesting + 1

            # Break/continue add 1
            if re.search(r"\b(break|continue)\b", stripped):
                complexity += 1

        return complexity

    def _get_severity(self, complexity: int, threshold: int) -> Severity:
        """Determine severity based on cognitive complexity.

        Args:
            complexity: Actual complexity value.
            threshold: Maximum allowed complexity.

        Returns:
            Appropriate severity level.
        """
        ratio = complexity / max(threshold, 1)
        if ratio >= 3.0:
            return Severity.CRITICAL
        elif ratio >= 2.0:
            return Severity.HIGH
        elif ratio >= 1.0:
            return Severity.MEDIUM
        return Severity.LOW


class DeepNestingRule(BaseRule):
    """Detects code with excessive nesting depth.

    Deep nesting makes code harder to read and understand.
    This rule checks for nesting levels beyond a configurable threshold.

    Threshold is configurable via 'max_nesting_depth' (default: 4).
    """

    id = "CC003"
    name = "Deep Nesting"
    description = "Code with excessive nesting depth is hard to read and maintain."
    severity = Severity.MEDIUM
    category = "complexity"
    languages = ["python", "javascript", "typescript", "go"]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for deep nesting.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []
        max_depth = self.get_config("max_nesting_depth", 4)

        if language == "python":
            issues = self._check_python(content, file_path, max_depth)
        else:
            issues = self._check_generic(content, file_path, language, max_depth)

        return issues

    def _check_python(self, content: str, file_path: str, max_depth: int) -> List[Issue]:
        """Check Python code for deep nesting using AST.

        Args:
            content: Python source code.
            file_path: Path to the file.
            max_depth: Maximum allowed nesting depth.

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
                max_nesting = self._compute_python_nesting_depth(node, 0)
                if max_nesting > max_depth:
                    line_num = node.lineno
                    snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=Severity.MEDIUM if max_nesting <= max_depth + 2 else Severity.HIGH,
                        message=(
                            f"Function '{node.name}' has nesting depth of {max_nesting} "
                            f"(threshold: {max_depth}). Consider flattening the code."
                        ),
                        file_path=file_path,
                        line=line_num,
                        code_snippet=snippet.strip(),
                        suggestion="Use early returns, guard clauses, or extract nested logic into helper functions.",
                        category=self.category,
                        language="python",
                    ))

        return issues

    def _compute_python_nesting_depth(self, node: ast.AST, current_depth: int) -> int:
        """Compute maximum nesting depth in a Python AST node.

        Args:
            node: AST node to analyze.
            current_depth: Current nesting depth.

        Returns:
            Maximum nesting depth found.
        """
        max_depth = current_depth

        nesting_nodes = (
            ast.If, ast.For, ast.While, ast.With, ast.Try,
            ast.AsyncFor, ast.AsyncWith,
        )

        for child in ast.iter_child_nodes(node):
            if isinstance(child, nesting_nodes):
                child_depth = self._compute_python_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            elif isinstance(child, (ast.ExceptHandler,)):
                child_depth = self._compute_python_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._compute_python_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _check_generic(self, content: str, file_path: str, language: str,
                       max_depth: int) -> List[Issue]:
        """Check non-Python code for deep nesting using indentation.

        Args:
            content: Source code content.
            file_path: Path to the file.
            language: Programming language.
            max_depth: Maximum allowed nesting depth.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()

        # Detect indent unit (2 or 4 spaces, or tabs)
        indent_unit = self._detect_indent_unit(lines)

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("*"):
                continue

            indent = len(line) - len(line.lstrip())
            if indent_unit > 0:
                depth = indent // indent_unit
            else:
                depth = 0

            if depth > max_depth:
                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=Severity.MEDIUM if depth <= max_depth + 2 else Severity.HIGH,
                    message=(
                        f"Code has nesting depth of {depth} (threshold: {max_depth}). "
                        f"Consider flattening the control flow."
                    ),
                    file_path=file_path,
                    line=i + 1,
                    code_snippet=stripped,
                    suggestion="Use early returns, guard clauses, or extract nested logic.",
                    category=self.category,
                    language=language,
                ))

        return issues

    def _detect_indent_unit(self, lines: List[str]) -> int:
        """Detect the indentation unit used in the file.

        Args:
            lines: List of source code lines.

        Returns:
            Number of spaces per indent level (2 or 4), or 0 if tabs are used.
        """
        indents = []
        for line in lines:
            if line.strip() and line[0] in (" ", "\t"):
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indents.append(indent)

        if not indents:
            return 4  # Default

        # Find the most common smallest indent
        from collections import Counter
        non_zero = [i for i in indents if i > 0]
        if not non_zero:
            return 4

        counter = Counter(non_zero)
        most_common = counter.most_common(1)[0][0]

        # Determine if it's 2-space or 4-space
        if most_common <= 2:
            return 2
        return 4
