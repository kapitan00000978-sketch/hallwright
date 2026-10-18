"""
Hallwright Enterprise Security: ReDoS (Regular Expression Denial of Service) Sanitizer.
Part of Pillar IV: Enterprise Modular Domain Libraries (Bosqich 45).

Audits regex strings for catastrophic backtracking patterns that can hang or crash
production servers when fed adversarial payload inputs.
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ReDoSFinding:
    pattern: str
    vulnerability_type: str
    risk_level: str
    description: str
    suggestion: str


class ReDoSSanitizer:
    """
    Static analyzer for detecting catastrophic polynomial and exponential backtracking in regular expressions.
    """

    # Vulnerability signatures
    # 1. Nested quantifiers: e.g. (a+)+, (.*a)*, ([a-z]+)+
    NESTED_QUANTIFIERS = re.compile(r"\((?:[^\)]*(?:\+|\*|\{\d+,?\d*\}))[^\)]*\)(?:\+|\*|\{\d+,?\d*\})")

    # 2. Alternations inside repetition with overlap risk: e.g. (a|aa)+, (.*|.*)
    OVERLAPPING_ALTERNATIONS = re.compile(r"\((?:[a-zA-Z0-9_\-\s]+\|[a-zA-Z0-9_\-\s]+)\)(?:\+|\*|\{\d+,?\d*\})")

    @classmethod
    def audit_pattern(cls, pattern_str: str) -> List[ReDoSFinding]:
        """Audits a regular expression string for catastrophic backtracking vulnerabilities."""
        findings: List[ReDoSFinding] = []

        # Check nested quantifiers
        match_nested = cls.NESTED_QUANTIFIERS.search(pattern_str)
        if match_nested:
            findings.append(ReDoSFinding(
                pattern=pattern_str,
                vulnerability_type="NESTED_QUANTIFIER",
                risk_level="CRITICAL",
                description=f"Nested quantifier detected at '{match_nested.group(0)}'. This leads to exponential O(2^N) backtracking.",
                suggestion="Eliminate nested repetitions or use atomic groupings / possessive quantifiers."
            ))

        # Check overlapping alternations
        match_overlap = cls.OVERLAPPING_ALTERNATIONS.search(pattern_str)
        if match_overlap:
            # Check if alternations share prefixes
            inner = match_overlap.group(0)[1:].split(")")[0]
            parts = inner.split("|")
            if len(parts) >= 2:
                p0, p1 = parts[0].strip(), parts[1].strip()
                if p0 and p1 and (p0.startswith(p1) or p1.startswith(p0)):
                    findings.append(ReDoSFinding(
                        pattern=pattern_str,
                        vulnerability_type="OVERLAPPING_ALTERNATION",
                        risk_level="HIGH",
                        description=f"Overlapping alternation with repetition detected: '{match_overlap.group(0)}'.",
                        suggestion="Disambiguate alternation clauses to ensure prefixes are mutually exclusive."
                    ))

        return findings

    @classmethod
    def is_safe(cls, pattern_str: str) -> bool:
        """Returns True if no critical or high risk ReDoS patterns are detected."""
        return len(cls.audit_pattern(pattern_str)) == 0
