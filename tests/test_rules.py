"""
Tests for individual rules.

Tests each rule independently to ensure correct detection logic.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coderefactor_pilot.rules.complexity import CyclomaticComplexityRule, CognitiveComplexityRule, DeepNestingRule
from coderefactor_pilot.rules.naming import SnakeCaseNamingRule, PascalCaseClassRule, ShortIdentifierRule
from coderefactor_pilot.rules.duplication import DuplicateCodeBlockRule, SimilarFunctionRule
from coderefactor_pilot.rules.security import HardcodedPasswordRule, SQLInjectionRule, DangerousFunctionRule
from coderefactor_pilot.rules.style import LineLengthRule, FunctionLengthRule, TooManyParametersRule
from coderefactor_pilot.rules.performance import StringConcatenationInLoopRule, InefficientDataTypeRule
from coderefactor_pilot.rules.base import Severity


class TestComplexityRules(unittest.TestCase):
    """Test cases for complexity rules."""

    def test_cyclomatic_complexity_python(self):
        """Test cyclomatic complexity detection for Python."""
        code = '''
def simple():
    return 1

def complex_func(a, b, c, d, e):
    if a:
        if b:
            if c:
                for x in range(10):
                    if x > 5:
                        while d:
                            d -= 1
                    elif x < 2:
                        pass
                    else:
                        continue
            elif c < 0:
                pass
        else:
            for y in range(5):
                if y:
                    pass
    elif a < 0:
        if b < 0:
            pass
    try:
        e = int(c)
    except ValueError:
        pass
    return a
'''
        rule = CyclomaticComplexityRule(config={"max_complexity": 5})
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)

    def test_cyclomatic_complexity_javascript(self):
        """Test cyclomatic complexity detection for JavaScript."""
        code = '''
function simple() {
    return 1;
}

function complexFunc(a, b, c) {
    if (a > 0) {
        if (b > 0) {
            for (var i = 0; i < 10; i++) {
                if (i % 2 === 0 && c > 0) {
                    while (a > 0) {
                        a--;
                    }
                } else if (i % 3 === 0) {
                    continue;
                }
            }
        } else {
            switch(b) {
                case 1: break;
                case 2: break;
                default: break;
            }
        }
    }
    return a;
}
'''
        rule = CyclomaticComplexityRule(config={"max_complexity": 5})
        issues = rule.check(code, "test.js", "javascript")
        self.assertGreater(len(issues), 0)

    def test_deep_nesting_python(self):
        """Test deep nesting detection for Python."""
        code = '''
def deeply_nested():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        if True:
                            pass
'''
        rule = DeepNestingRule(config={"max_nesting_depth": 3})
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)

    def test_cognitive_complexity_python(self):
        """Test cognitive complexity detection for Python."""
        code = '''
def cognitive_complex(x, y, z):
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
                        continue
                    else:
                        pass
            else:
                for j in range(5):
                    if j > 2:
                        pass
        else:
            pass
'''
        rule = CognitiveComplexityRule(config={"max_cognitive_complexity": 5})
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)


class TestNamingRules(unittest.TestCase):
    """Test cases for naming rules."""

    def test_snake_case_violations(self):
        """Test snake_case naming detection."""
        code = '''
def BadFunc():
    pass

myVar = 10
anotherBad = 20
good_var = 30
'''
        rule = SnakeCaseNamingRule()
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)

    def test_pascal_case_class_violations(self):
        """Test PascalCase class naming detection."""
        code = '''
class my_class:
    pass

class bad_Class:
    pass

class GoodClass:
    pass
'''
        rule = PascalCaseClassRule()
        issues = rule.check(code, "test.py", "python")
        self.assertEqual(len(issues), 2)

    def test_short_identifier(self):
        """Test short identifier detection."""
        code = '''
x = calculateSomething()
a = doSomethingElse()
i = 0  # This should be acceptable
'''
        rule = ShortIdentifierRule()
        issues = rule.check(code, "test.py", "python")
        # x and a should be flagged, i should not
        self.assertGreater(len(issues), 0)


class TestSecurityRules(unittest.TestCase):
    """Test cases for security rules."""

    def test_hardcoded_password(self):
        """Test hardcoded password detection."""
        code = '''
password = "super_secret"
API_KEY = "abc123"
token = "bearer_token_xyz"
'''
        rule = HardcodedPasswordRule()
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)
        for issue in issues:
            self.assertEqual(issue.severity, Severity.CRITICAL)

    def test_sql_injection(self):
        """Test SQL injection detection."""
        code = '''
query = "SELECT * FROM users WHERE id = " + user_id
cursor.execute(f"DELETE FROM items WHERE name = '{name}'")
'''
        rule = SQLInjectionRule()
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)

    def test_dangerous_functions(self):
        """Test dangerous function detection."""
        code = '''
eval(user_input)
exec(code_string)
pickle.loads(data)
os.system("ls")
'''
        rule = DangerousFunctionRule()
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)

    def test_dangerous_functions_javascript(self):
        """Test dangerous function detection for JavaScript."""
        code = '''
eval(userInput);
document.write(htmlContent);
innerHTML = "<script>alert('xss')</script>";
setTimeout("alert(1)", 1000);
'''
        rule = DangerousFunctionRule()
        issues = rule.check(code, "test.js", "javascript")
        self.assertGreater(len(issues), 0)


class TestStyleRules(unittest.TestCase):
    """Test cases for style rules."""

    def test_line_length(self):
        """Test line length detection."""
        long_line = "x" * 200
        code = f"def func():\n    {long_line}\n"
        rule = LineLengthRule(config={"max_line_length": 120})
        issues = rule.check(code, "test.py", "python")
        self.assertEqual(len(issues), 1)

    def test_function_length(self):
        """Test function length detection."""
        lines = ["    pass"] * 60
        code = "def long_function():\n" + "\n".join(lines) + "\n"
        rule = FunctionLengthRule(config={"max_function_length": 50})
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)

    def test_too_many_parameters(self):
        """Test parameter count detection."""
        code = '''
def func(a, b, c, d, e, f, g, h, i):
    pass
'''
        rule = TooManyParametersRule(config={"max_parameters": 7})
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)


class TestPerformanceRules(unittest.TestCase):
    """Test cases for performance rules."""

    def test_string_concat_in_loop(self):
        """Test string concatenation in loop detection."""
        code = '''
def build(items):
    result = ""
    for item in items:
        result += str(item)
    return result
'''
        rule = StringConcatenationInLoopRule()
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)

    def test_inefficient_data_type(self):
        """Test inefficient data type detection."""
        code = '''
def check(item):
    if item in ["a", "b", "c", "d", "e", "f", "g", "h"]:
        return True
    return False
'''
        rule = InefficientDataTypeRule()
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)


class TestDuplicationRules(unittest.TestCase):
    """Test cases for duplication rules."""

    def test_duplicate_code_blocks(self):
        """Test duplicate code block detection."""
        code = '''
def func_a(x, y):
    result = x + y
    if result > 10:
        return result * 2
    else:
        return result / 2

def func_b(a, b):
    result = a + b
    if result > 10:
        return result * 2
    else:
        return result / 2
'''
        rule = DuplicateCodeBlockRule(config={"min_duplicate_lines": 4})
        issues = rule.check(code, "test.py", "python")
        self.assertGreater(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
