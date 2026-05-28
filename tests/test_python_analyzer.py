"""
Tests for the Python analyzer module.

Tests the PythonAnalyzer with various code samples to ensure
rules are correctly applied and issues are detected.
"""

import os
import sys
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coderefactor_pilot.analyzer.python_analyzer import PythonAnalyzer
from coderefactor_pilot.rules.base import Severity


class TestPythonAnalyzer(unittest.TestCase):
    """Test cases for the Python analyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "max_line_length": 120,
            "max_function_length": 50,
            "max_file_length": 500,
            "max_parameters": 7,
            "max_complexity": 10,
            "max_cognitive_complexity": 15,
            "max_nesting_depth": 4,
            "min_duplicate_lines": 6,
        }
        self.analyzer = PythonAnalyzer(config=self.config)

    def test_cyclomatic_complexity_detection(self):
        """Test that high cyclomatic complexity is detected."""
        code = '''
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                for i in range(10):
                    if i % 2 == 0:
                        while x > 0:
                            x -= 1
                            if x == 5:
                                break
                    elif i % 3 == 0:
                        pass
                    else:
                        continue
            else:
                for j in range(5):
                    if j > 2:
                        pass
        else:
            pass
    elif x < 0:
        if y < 0:
            pass
    else:
        pass
    try:
        x = int(z)
    except ValueError:
        pass
    except TypeError:
        pass
    return x
'''
        issues = self.analyzer.analyze("test.py")
        # Write code to a temp file and analyze
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            cc_issues = [i for i in issues if i.rule_id == "CC001"]
            self.assertGreater(len(cc_issues), 0, "Should detect high cyclomatic complexity")
            self.assertEqual(cc_issues[0].language, "python")
        finally:
            os.unlink(temp_path)

    def test_naming_snake_case(self):
        """Test that non-snake-case function names are detected."""
        code = '''
def BadFunctionName():
    pass

def anotherBadOne():
    pass

def good_function_name():
    pass
'''
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            naming_issues = [i for i in issues if i.rule_id == "NM001"]
            self.assertEqual(len(naming_issues), 2, "Should detect 2 naming violations")
        finally:
            os.unlink(temp_path)

    def test_pascal_case_class(self):
        """Test that non-PascalCase class names are detected."""
        code = '''
class my_class:
    pass

class Another_Bad_Class:
    pass

class GoodClass:
    pass
'''
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            class_issues = [i for i in issues if i.rule_id == "NM002"]
            self.assertEqual(len(class_issues), 2, "Should detect 2 class naming violations")
        finally:
            os.unlink(temp_path)

    def test_hardcoded_password(self):
        """Test that hardcoded passwords are detected."""
        code = '''
password = "my_secret_password_123"
api_key = "sk-1234567890abcdef"
SECRET_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxx"
'''
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            sec_issues = [i for i in issues if i.rule_id == "SEC001"]
            self.assertGreater(len(sec_issues), 0, "Should detect hardcoded secrets")
            # Check severity is CRITICAL
            for issue in sec_issues:
                self.assertEqual(issue.severity, Severity.CRITICAL)
        finally:
            os.unlink(temp_path)

    def test_sql_injection(self):
        """Test that SQL injection risks are detected."""
        code = '''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    cursor.execute(query)
    return cursor.fetchall()
'''
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            sql_issues = [i for i in issues if i.rule_id == "SEC002"]
            self.assertGreater(len(sql_issues), 0, "Should detect SQL injection risk")
        finally:
            os.unlink(temp_path)

    def test_dangerous_functions(self):
        """Test that dangerous function usage is detected."""
        code = '''
def unsafe():
    data = eval(input("Enter: "))
    exec("print('hello')")
    result = pickle.loads(data)
    os.system("rm -rf /")
'''
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            danger_issues = [i for i in issues if i.rule_id == "SEC003"]
            self.assertGreater(len(danger_issues), 0, "Should detect dangerous functions")
        finally:
            os.unlink(temp_path)

    def test_line_length(self):
        """Test that lines exceeding max length are detected."""
        code = '''
def function_with_a_very_long_name_that_exceeds_the_maximum_allowed_line_length_of_one_hundred_and_twenty_characters(x, y, z):
    pass
'''
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            length_issues = [i for i in issues if i.rule_id == "STY001"]
            self.assertGreater(len(length_issues), 0, "Should detect long lines")
        finally:
            os.unlink(temp_path)

    def test_trailing_whitespace(self):
        """Test that trailing whitespace is detected."""
        code = 'def hello():\n    x = 1   \n    return x\n'
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            ws_issues = [i for i in issues if i.rule_id == "STY005"]
            self.assertGreater(len(ws_issues), 0, "Should detect trailing whitespace")
        finally:
            os.unlink(temp_path)

    def test_missing_docstring(self):
        """Test that missing docstrings are detected."""
        code = '''
class MyClass:
    def public_method(self):
        pass

    def _private_method(self):
        pass
'''
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            doc_issues = [i for i in issues if i.rule_id == "STY006"]
            # Should detect class and public_method but not _private_method
            self.assertGreater(len(doc_issues), 0, "Should detect missing docstrings")
            for issue in doc_issues:
                self.assertNotIn("_private_method", issue.message)
        finally:
            os.unlink(temp_path)

    def test_unused_imports(self):
        """Test that unused imports are detected."""
        code = '''
import os
import sys
import json

def hello():
    print("hello")
'''
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            import_issues = [i for i in issues if i.rule_id == "PERF006"]
            self.assertGreater(len(import_issues), 0, "Should detect unused imports")
        finally:
            os.unlink(temp_path)

    def test_clean_code_no_issues(self):
        """Test that clean code produces minimal issues."""
        code = '''"""Module docstring."""


def add(a, b):
    """Add two numbers."""
    return a + b


def greet(name):
    """Greet a person by name."""
    return f"Hello, {name}!"
'''
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            # Clean code should have very few issues
            high_sev = [i for i in issues if i.severity.value in ("high", "critical")]
            self.assertEqual(len(high_sev), 0, "Clean code should have no high/critical issues")
        finally:
            os.unlink(temp_path)

    def test_string_concatenation_in_loop(self):
        """Test that string concatenation in loops is detected."""
        code = '''
def build_string(items):
    result = ""
    for item in items:
        result += str(item)
    return result
'''
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name

        try:
            issues = self.analyzer.analyze(temp_path)
            perf_issues = [i for i in issues if i.rule_id == "PERF001"]
            self.assertGreater(len(perf_issues), 0, "Should detect string concat in loop")
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
