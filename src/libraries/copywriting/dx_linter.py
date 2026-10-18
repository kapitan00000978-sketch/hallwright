"""Hallwright Enterprise Copywriting Library: Developer Experience (DX) Linter.

Audits documentation, CLI messages, and error diagnostics against readability,
empathy, and actionable ergonomics standards.
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class DXLintIssue:
    """Represents a DX friction point or stylistic flaw."""
    rule: str
    severity: str
    message: str
    suggestion: str


class DXLinter:
    """Developer Experience & Readability Auditor."""

    @staticmethod
    def count_syllables(word: str) -> int:
        """Estimate syllable count in an English word."""
        word = word.lower().strip()
        if len(word) <= 3:
            return 1
        word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
        word = re.sub(r'^y', '', word)
        matches = re.findall(r'[aeiouy]{1,2}', word)
        return max(1, len(matches))

    @classmethod
    def calculate_flesch_reading_ease(cls, text: str) -> float:
        """Compute the Flesch Reading Ease score (0 to 100+).

        Scores:
        90-100: Very Easy
        60-70: Plain English
        0-30: Very Difficult / Academic
        """
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = [w.strip() for w in re.findall(r'\b[a-zA-Z]+\b', text) if w.strip()]

        if not sentences or not words:
            return 100.0

        num_sentences = len(sentences)
        num_words = len(words)
        num_syllables = sum(cls.count_syllables(w) for w in words)

        asl = num_words / num_sentences
        asw = num_syllables / num_words

        score = 206.835 - (1.015 * asl) - (84.6 * asw)
        return round(score, 2)

    @classmethod
    def audit_error_message(cls, message: str) -> List[DXLintIssue]:
        """Audit an error diagnostic for actionable ergonomics."""
        issues: List[DXLintIssue] = []

        if not message or not message.strip():
            issues.append(
                DXLintIssue(
                    rule="DX-001",
                    severity="HIGH",
                    message="Error message is empty.",
                    suggestion="Provide a clear description of the failure and how to resolve it.",
                )
            )
            return issues

        # Check for vague phrases
        vague_terms = ["something went wrong", "an error occurred", "failed", "invalid input"]
        lower_msg = message.lower().strip()
        for term in vague_terms:
            if lower_msg == term or lower_msg == f"{term}.":
                issues.append(
                    DXLintIssue(
                        rule="DX-002",
                        severity="MEDIUM",
                        message=f"Error message contains vague phrasing: '{term}'.",
                        suggestion="Explain *why* the failure happened and what valid input looks like.",
                    )
                )

        # Check for actionable guidance
        has_guidance = any(k in lower_msg for k in ["try", "ensure", "check", "run", "pass", "expected"])
        if not has_guidance and len(message.split()) > 5:
            issues.append(
                DXLintIssue(
                    rule="DX-003",
                    severity="LOW",
                    message="Error message lacks actionable remediation hint.",
                    suggestion="Add a suggested next action (e.g., 'Try passing --config path/to/file').",
                )
            )

        return issues
