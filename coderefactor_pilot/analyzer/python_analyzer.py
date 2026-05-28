"""
Python code analyzer.

Provides the main analyzer for Python source code, with all applicable
rules pre-configured.
"""

from typing import Any, Dict, List, Optional

from coderefactor_pilot.analyzer.base import BaseAnalyzer
from coderefactor_pilot.rules.base import BaseRule
from coderefactor_pilot.rules.complexity import CyclomaticComplexityRule, CognitiveComplexityRule, DeepNestingRule
from coderefactor_pilot.rules.naming import SnakeCaseNamingRule, PascalCaseClassRule, ShortIdentifierRule
from coderefactor_pilot.rules.duplication import DuplicateCodeBlockRule, SimilarFunctionRule
from coderefactor_pilot.rules.security import (
    HardcodedPasswordRule, SQLInjectionRule, DangerousFunctionRule,
    InsecureRandomRule, HardcodedURLRule,
)
from coderefactor_pilot.rules.style import (
    LineLengthRule, FunctionLengthRule, FileLengthRule,
    TooManyParametersRule, TrailingWhitespaceRule, MissingDocstringRule,
)
from coderefactor_pilot.rules.performance import (
    StringConcatenationInLoopRule, UnnecessaryListCopyRule,
    GlobalVariableLookupRule, InefficientDataTypeRule,
    LazyImportRule, UnusedImportRule,
)


class PythonAnalyzer(BaseAnalyzer):
    """Analyzer for Python source code.

    Pre-configured with all rules applicable to Python:
    - Complexity rules (cyclomatic, cognitive, nesting)
    - Naming rules (snake_case, PascalCase, short names)
    - Duplication rules (duplicate blocks, similar functions)
    - Security rules (hardcoded secrets, SQL injection, dangerous functions)
    - Style rules (line length, function length, docstrings)
    - Performance rules (string concat, unused imports, etc.)
    """

    language = "python"

    def __init__(self, rules: Optional[List[BaseRule]] = None,
                 config: Optional[Dict[str, Any]] = None):
        """Initialize the Python analyzer.

        Args:
            rules: Optional custom list of rules. If None, uses all Python rules.
            config: Configuration dictionary for rule thresholds.
        """
        if rules is None:
            rules = self._get_default_rules(config)
        super().__init__(rules=rules, config=config)

    @staticmethod
    def _get_default_rules(config: Optional[Dict[str, Any]] = None) -> List[BaseRule]:
        """Create the default set of rules for Python analysis.

        Args:
            config: Configuration dictionary.

        Returns:
            List of default rules.
        """
        rule_config = config or {}

        return [
            # Complexity rules
            CyclomaticComplexityRule(config=rule_config),
            CognitiveComplexityRule(config=rule_config),
            DeepNestingRule(config=rule_config),

            # Naming rules
            SnakeCaseNamingRule(config=rule_config),
            PascalCaseClassRule(config=rule_config),
            ShortIdentifierRule(config=rule_config),

            # Duplication rules
            DuplicateCodeBlockRule(config=rule_config),
            SimilarFunctionRule(config=rule_config),

            # Security rules
            HardcodedPasswordRule(config=rule_config),
            SQLInjectionRule(config=rule_config),
            DangerousFunctionRule(config=rule_config),
            InsecureRandomRule(config=rule_config),
            HardcodedURLRule(config=rule_config),

            # Style rules
            LineLengthRule(config=rule_config),
            FunctionLengthRule(config=rule_config),
            FileLengthRule(config=rule_config),
            TooManyParametersRule(config=rule_config),
            TrailingWhitespaceRule(config=rule_config),
            MissingDocstringRule(config=rule_config),

            # Performance rules
            StringConcatenationInLoopRule(config=rule_config),
            UnnecessaryListCopyRule(config=rule_config),
            GlobalVariableLookupRule(config=rule_config),
            InefficientDataTypeRule(config=rule_config),
            LazyImportRule(config=rule_config),
            UnusedImportRule(config=rule_config),
        ]
