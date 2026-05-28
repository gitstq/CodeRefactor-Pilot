"""
Go code analyzer.

Provides the analyzer for Go source code with all applicable rules.
"""

from typing import Any, Dict, List, Optional

from coderefactor_pilot.analyzer.base import BaseAnalyzer
from coderefactor_pilot.rules.base import BaseRule
from coderefactor_pilot.rules.complexity import CyclomaticComplexityRule, CognitiveComplexityRule, DeepNestingRule
from coderefactor_pilot.rules.naming import GoNamingRule, ShortIdentifierRule
from coderefactor_pilot.rules.duplication import DuplicateCodeBlockRule
from coderefactor_pilot.rules.security import (
    HardcodedPasswordRule, SQLInjectionRule, DangerousFunctionRule,
    HardcodedURLRule,
)
from coderefactor_pilot.rules.style import (
    LineLengthRule, FunctionLengthRule, FileLengthRule,
    TooManyParametersRule, TrailingWhitespaceRule,
)
from coderefactor_pilot.rules.performance import StringConcatenationInLoopRule


class GoAnalyzer(BaseAnalyzer):
    """Analyzer for Go source code.

    Pre-configured with all rules applicable to Go:
    - Complexity rules (cyclomatic, cognitive, nesting)
    - Naming rules (Go naming conventions, short names)
    - Duplication rules (duplicate blocks)
    - Security rules (hardcoded secrets, SQL injection, dangerous functions)
    - Style rules (line length, function length, etc.)
    - Performance rules (string concatenation in loops)
    """

    language = "go"

    def __init__(self, rules: Optional[List[BaseRule]] = None,
                 config: Optional[Dict[str, Any]] = None):
        """Initialize the Go analyzer.

        Args:
            rules: Optional custom list of rules. If None, uses all Go rules.
            config: Configuration dictionary for rule thresholds.
        """
        if rules is None:
            rules = self._get_default_rules(config)
        super().__init__(rules=rules, config=config)

    @staticmethod
    def _get_default_rules(config: Optional[Dict[str, Any]] = None) -> List[BaseRule]:
        """Create the default set of rules for Go analysis.

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
            GoNamingRule(config=rule_config),
            ShortIdentifierRule(config=rule_config),

            # Duplication rules
            DuplicateCodeBlockRule(config=rule_config),

            # Security rules
            HardcodedPasswordRule(config=rule_config),
            SQLInjectionRule(config=rule_config),
            DangerousFunctionRule(config=rule_config),
            HardcodedURLRule(config=rule_config),

            # Style rules
            LineLengthRule(config=rule_config),
            FunctionLengthRule(config=rule_config),
            FileLengthRule(config=rule_config),
            TooManyParametersRule(config=rule_config),
            TrailingWhitespaceRule(config=rule_config),

            # Performance rules
            StringConcatenationInLoopRule(config=rule_config),
        ]
