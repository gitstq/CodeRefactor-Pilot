"""
Security issue detection rules.

Detects common security vulnerabilities including hardcoded passwords/tokens,
SQL injection risks, dangerous function usage (eval, exec, pickle), and more.
"""

import ast
import re
from typing import List

from coderefactor_pilot.rules.base import BaseRule, Issue, Severity


class HardcodedPasswordRule(BaseRule):
    """Detects hardcoded passwords, API keys, tokens, and secrets.

    Looks for common patterns like assigning string literals to variables
    with security-related names, or using string literals directly in
    authentication contexts.
    """

    id = "SEC001"
    name = "Hardcoded Password/Secret"
    description = "Detects hardcoded passwords, API keys, tokens, and other secrets in source code."
    severity = Severity.CRITICAL
    category = "security"
    languages = ["python", "javascript", "typescript", "go"]

    # Patterns for variable names that suggest secrets
    SECRET_NAME_PATTERNS = [
        r"(?i)(password|passwd|pwd)",
        r"(?i)(secret|api_key|apikey|api_secret)",
        r"(?i)(token|access_token|auth_token|refresh_token)",
        r"(?i)(private_key|secret_key|signing_key)",
        r"(?i)(credential|auth|session_key)",
        r"(?i)(db_password|database_password)",
        r"(?i)(encryption_key|decrypt_key)",
    ]

    # Patterns for string values that look like secrets
    SECRET_VALUE_PATTERNS = [
        r"(?i)password\s*=\s*['\"][^'\"]+['\"]",
        r"(?i)api_key\s*=\s*['\"][^'\"]+['\"]",
        r"(?i)apikey\s*=\s*['\"][^'\"]+['\"]",
        r"(?i)secret\s*=\s*['\"][^'\"]+['\"]",
        r"(?i)token\s*=\s*['\"][^'\"]+['\"]",
        r"(?i)private_key\s*=\s*['\"][^'\"]+['\"]",
        r"(?i)auth_token\s*=\s*['\"][^'\"]+['\"]",
    ]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for hardcoded secrets.

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
        """Check Python code for hardcoded secrets using AST.

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
                        var_name = target.id
                        if self._is_secret_name(var_name) and isinstance(node.value, ast.Constant):
                            value = node.value.value
                            if isinstance(value, str) and len(value) > 0:
                                line_num = node.lineno
                                snippet = lines[line_num - 1] if line_num <= len(lines) else ""
                                # Mask the actual value
                                masked = value[:3] + "***" if len(value) > 3 else "***"
                                issues.append(Issue(
                                    rule_id=self.id,
                                    rule_name=self.name,
                                    severity=self.severity,
                                    message=(
                                        f"Hardcoded secret detected: variable '{var_name}' "
                                        f"contains a hardcoded string value ('{masked}'). "
                                        f"Use environment variables or a secret manager."
                                    ),
                                    file_path=file_path,
                                    line=line_num,
                                    code_snippet=snippet.strip(),
                                    suggestion=(
                                        f"Move '{var_name}' to an environment variable "
                                        f"or use a secrets management system."
                                    ),
                                    category=self.category,
                                    language="python",
                                ))

        return issues

    def _check_generic(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check non-Python code for hardcoded secrets using regex.

        Args:
            content: Source code content.
            file_path: Path to the file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("*"):
                continue

            for pattern in self.SECRET_VALUE_PATTERNS:
                if re.search(pattern, stripped):
                    # Extract the variable name
                    match = re.search(r"(\w+)\s*=\s*['\"]", stripped)
                    var_name = match.group(1) if match else "unknown"
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=(
                            f"Potential hardcoded secret: '{var_name}' is assigned "
                            f"a string literal. Use environment variables instead."
                        ),
                        file_path=file_path,
                        line=i + 1,
                        code_snippet=stripped[:80] + ("..." if len(stripped) > 80 else ""),
                        suggestion=f"Use environment variables or a secret manager for '{var_name}'.",
                        category=self.category,
                        language=language,
                    ))
                    break  # One issue per line

        return issues

    def _is_secret_name(self, name: str) -> bool:
        """Check if a variable name suggests it holds a secret.

        Args:
            name: Variable name to check.

        Returns:
            True if the name matches secret-related patterns.
        """
        for pattern in self.SECRET_NAME_PATTERNS:
            if re.search(pattern, name):
                return True
        return False


class SQLInjectionRule(BaseRule):
    """Detects potential SQL injection vulnerabilities.

    Looks for string formatting/concatenation used in SQL queries
    instead of parameterized queries.
    """

    id = "SEC002"
    name = "SQL Injection Risk"
    description = "Detects potential SQL injection vulnerabilities from string formatting in queries."
    severity = Severity.CRITICAL
    category = "security"
    languages = ["python", "javascript", "typescript", "go"]

    # SQL keywords that suggest a query
    SQL_PATTERNS = [
        r"(?i)\bSELECT\b.*\bFROM\b",
        r"(?i)\bINSERT\b.*\bINTO\b",
        r"(?i)\bUPDATE\b.*\bSET\b",
        r"(?i)\bDELETE\b.*\bFROM\b",
        r"(?i)\bDROP\b.*\bTABLE\b",
        r"(?i)\bCREATE\b.*\bTABLE\b",
    ]

    # Dangerous string formatting patterns
    FORMAT_PATTERNS_PYTHON = [
        r"\.format\s*\(",
        r"%\s*[\w]",
        r"f['\"]",
        r"\+\s*(?:str\s*\(|f['\"])",  # String concat with str() or f-string
    ]

    FORMAT_PATTERNS_GENERIC = [
        r"\+\s*['\"]",  # String concatenation
        r"\$\{",  # Template literal interpolation
        r"`[^`]*\$\{",  # Template string
    ]

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for SQL injection risks.

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
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("#"):
                continue

            # Check if line contains SQL
            has_sql = False
            for sql_pattern in self.SQL_PATTERNS:
                if re.search(sql_pattern, stripped):
                    has_sql = True
                    break

            if not has_sql:
                continue

            # Check for string formatting/concatenation in SQL context
            if language == "python":
                dangerous = any(
                    re.search(p, stripped) for p in self.FORMAT_PATTERNS_PYTHON
                )
            else:
                dangerous = any(
                    re.search(p, stripped) for p in self.FORMAT_PATTERNS_GENERIC
                )

            if dangerous:
                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message=(
                        "Potential SQL injection: string formatting/concatenation "
                        "detected in SQL query. Use parameterized queries instead."
                    ),
                    file_path=file_path,
                    line=i + 1,
                    code_snippet=stripped[:100] + ("..." if len(stripped) > 100 else ""),
                    suggestion="Use parameterized queries or an ORM to prevent SQL injection.",
                    category=self.category,
                    language=language,
                ))

        return issues


class DangerousFunctionRule(BaseRule):
    """Detects usage of dangerous functions that can lead to security issues.

    Checks for eval(), exec(), pickle.loads(), subprocess with shell=True,
    and other potentially dangerous operations.
    """

    id = "SEC003"
    name = "Dangerous Function Usage"
    description = "Detects usage of dangerous functions like eval(), exec(), pickle.loads()."
    severity = Severity.HIGH
    category = "security"
    languages = ["python", "javascript", "typescript", "go"]

    # Dangerous function patterns per language
    DANGEROUS_PATTERNS = {
        "python": [
            (r"\beval\s*\(", "eval()", "Use ast.literal_eval() for safe evaluation or restructure the code."),
            (r"\bexec\s*\(", "exec()", "Avoid exec(). If dynamic code execution is needed, use a safer alternative."),
            (r"pickle\.loads?\s*\(", "pickle.loads()", "pickle is insecure. Use json for serialization or implement safe deserialization."),
            (r"subprocess\.\w+\(.*shell\s*=\s*True", "subprocess with shell=True", "Avoid shell=True to prevent shell injection. Use a list of arguments instead."),
            (r"os\.system\s*\(", "os.system()", "Use subprocess.run() with a list of arguments instead of os.system()."),
            (r"yaml\.load\s*\(", "yaml.load()", "Use yaml.safe_load() instead to prevent arbitrary code execution."),
            (r"marshal\.loads?\s*\(", "marshal.loads()", "marshal is unsafe for untrusted data. Use safer serialization."),
            (r"__import__\s*\(", "__import__()", "Avoid dynamic imports with untrusted input."),
        ],
        "javascript": [
            (r"\beval\s*\(", "eval()", "Never use eval(). Use JSON.parse() for JSON data or Function constructor sparingly."),
            (r"\bnew\s+Function\s*\(", "new Function()", "Avoid creating functions from strings. Use regular function definitions."),
            (r"\bdocument\.write\s*\(", "document.write()", "document.write() can lead to XSS. Use DOM manipulation methods instead."),
            (r"\binnerHTML\s*=", "innerHTML assignment", "Setting innerHTML can lead to XSS. Use textContent or DOMPurify."),
            (r"\bsetTimeout\s*\(\s*['\"]", "setTimeout with string", "Avoid passing strings to setTimeout. Use function references instead."),
            (r"\bsetInterval\s*\(\s*['\"]", "setInterval with string", "Avoid passing strings to setInterval. Use function references instead."),
        ],
        "typescript": [
            (r"\beval\s*\(", "eval()", "Never use eval(). Use JSON.parse() for JSON data."),
            (r"\bnew\s+Function\s*\(", "new Function()", "Avoid creating functions from strings."),
            (r"\binnerHTML\s*=", "innerHTML assignment", "Setting innerHTML can lead to XSS. Use textContent or sanitize input."),
            (r"\bsetTimeout\s*\(\s*['\"]", "setTimeout with string", "Avoid passing strings to setTimeout."),
            (r"\bsetInterval\s*\(\s*['\"]", "setInterval with string", "Avoid passing strings to setInterval."),
        ],
        "go": [
            (r"\bexec\.Command\s*\(", "exec.Command", "Validate and sanitize all inputs passed to exec.Command."),
            (r"\bos/exec\.Command\s*\(", "os/exec.Command", "Validate and sanitize all inputs passed to exec.Command."),
        ],
    }

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for dangerous function usage.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()
        patterns = self.DANGEROUS_PATTERNS.get(language, [])

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            # Skip comments
            if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith("*"):
                continue

            for pattern, func_name, suggestion in patterns:
                if re.search(pattern, stripped):
                    issues.append(Issue(
                        rule_id=self.id,
                        rule_name=self.name,
                        severity=self.severity,
                        message=f"Dangerous function '{func_name}' detected. {suggestion}",
                        file_path=file_path,
                        line=i + 1,
                        code_snippet=stripped[:100] + ("..." if len(stripped) > 100 else ""),
                        suggestion=suggestion,
                        category=self.category,
                        language=language,
                    ))

        return issues


class InsecureRandomRule(BaseRule):
    """Detects usage of insecure random number generators for security purposes.

    Checks for use of random module (Python) or Math.random() (JS) in
    security-sensitive contexts like token generation or password creation.
    """

    id = "SEC004"
    name = "Insecure Random"
    description = "Detects insecure random number generators used in security-sensitive contexts."
    severity = Severity.HIGH
    category = "security"
    languages = ["python", "javascript", "typescript"]

    # Patterns suggesting security-sensitive context
    SECURITY_CONTEXT_PATTERNS = [
        r"(?i)(token|password|secret|key|nonce|salt|session|csrf|otp)",
        r"(?i)(generate|create|make|random)",
    ]

    # Insecure random patterns
    INSECURE_PATTERNS = {
        "python": [
            r"\brandom\.\w+\s*\(",
            r"import random",
        ],
        "javascript": [
            r"\bMath\.random\s*\(\s*\)",
        ],
        "typescript": [
            r"\bMath\.random\s*\(\s*\)",
        ],
    }

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for insecure random usage.

        Args:
            content: Source code content.
            file_path: Path to the source file.
            language: Programming language.

        Returns:
            List of issues found.
        """
        issues = []
        lines = content.splitlines()
        insecure_patterns = self.INSECURE_PATTERNS.get(language, [])

        # Check if file uses insecure random at all
        uses_insecure = False
        for line in lines:
            for pattern in insecure_patterns:
                if re.search(pattern, line):
                    uses_insecure = True
                    break
            if uses_insecure:
                break

        if not uses_insecure:
            return issues

        # Check for security-sensitive context
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue

            has_insecure = any(re.search(p, stripped) for p in insecure_patterns)
            has_security_ctx = any(re.search(p, stripped) for p in self.SECURITY_CONTEXT_PATTERNS)

            if has_insecure and has_security_ctx:
                if language == "python":
                    suggestion = "Use the 'secrets' module for security-sensitive random values."
                else:
                    suggestion = "Use the Web Crypto API (crypto.getRandomValues()) for security-sensitive random values."

                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message=(
                        "Insecure random number generator used in a security-sensitive context. "
                        f"{suggestion}"
                    ),
                    file_path=file_path,
                    line=i + 1,
                    code_snippet=stripped[:100],
                    suggestion=suggestion,
                    category=self.category,
                    language=language,
                ))

        return issues


class HardcodedURLRule(BaseRule):
    """Detects hardcoded URLs, especially internal/private service URLs.

    Internal URLs should be configurable via environment variables.
    """

    id = "SEC005"
    name = "Hardcoded URL"
    description = "Detects hardcoded URLs that should be configurable."
    severity = Severity.LOW
    category = "security"
    languages = ["python", "javascript", "typescript", "go"]

    URL_PATTERN = re.compile(
        r"(?:https?://|ftp://|ws://|wss://)(?:localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|"
        r"192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)[^\s'\"]*"
    )

    def check(self, content: str, file_path: str, language: str) -> List[Issue]:
        """Check code for hardcoded URLs.

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
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                continue

            match = self.URL_PATTERN.search(stripped)
            if match:
                url = match.group(0)
                # Truncate long URLs for display
                display_url = url[:60] + "..." if len(url) > 60 else url
                issues.append(Issue(
                    rule_id=self.id,
                    rule_name=self.name,
                    severity=self.severity,
                    message=f"Hardcoded internal/private URL detected: '{display_url}'. Make it configurable.",
                    file_path=file_path,
                    line=i + 1,
                    code_snippet=stripped[:100],
                    suggestion="Move URL to environment variables or configuration file.",
                    category=self.category,
                    language=language,
                ))

        return issues
