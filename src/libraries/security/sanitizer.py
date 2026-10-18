"""Hallwright Enterprise Security Library: Input Sanitizer & Defensive Guard.

Provides zero-trust recursive payload sanitization against Cross-Site Scripting (XSS),
SQL injection markers, path traversal attacks, and OS command injection vectors.
"""

import html
import re
import os
from typing import Any, Dict, List, Union


class SecuritySanitizationError(Exception):
    """Raised when an active malicious exploit vector is detected."""
    pass


class InputSanitizer:
    """Enterprise-grade recursive input sanitizer.

    Enforces strict sanitization rules:
    - HTML entity encoding for XSS prevention
    - SQL comment, tautology, and union pattern defense
    - Shell command metacharacter escape and detection
    - Path traversal neutralization ('../', '..\\')
    """

    # Dangerous SQL patterns
    _SQL_DANGEROUS = [
        re.compile(r"(--|/\*|\*/|;\s*$)", re.IGNORECASE),
        re.compile(r"(\bUNION\b.*\bSELECT\b)", re.IGNORECASE),
        re.compile(r"(\bOR\b\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"])", re.IGNORECASE),
        re.compile(r"(\bDROP\b\s+\bTABLE\b)", re.IGNORECASE),
        re.compile(r"(\bTRUNCATE\b\s+\bTABLE\b)", re.IGNORECASE),
    ]

    # Command injection metacharacters
    _CMD_DANGEROUS = re.compile(r"[;&|`$><]")

    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """Escape HTML control characters to prevent stored/reflected XSS."""
        if not isinstance(text, str):
            return text
        return html.escape(text, quote=True)

    @classmethod
    def detect_sql_injection(cls, query_string: str) -> bool:
        """Inspect a string for obvious SQL injection markers."""
        if not isinstance(query_string, str):
            return False
        for pattern in cls._SQL_DANGEROUS:
            if pattern.search(query_string):
                return True
        return False

    @classmethod
    def sanitize_path(cls, path_str: str, base_dir: str) -> str:
        """Neutralize directory traversal and ensure target path resides strictly inside base_dir."""
        normalized_base = os.path.abspath(base_dir)
        # Resolve target path relative to base
        combined = os.path.abspath(os.path.join(normalized_base, path_str.lstrip("/\\")))
        if not combined.startswith(normalized_base):
            raise SecuritySanitizationError(
                f"Path traversal detected: '{path_str}' attempts to escape base directory."
            )
        return combined

    @classmethod
    def clean_payload(cls, data: Any) -> Any:
        """Recursively sanitize strings inside nested dicts, lists, or primitives."""
        if isinstance(data, str):
            # Escapes HTML control characters by default
            return cls.sanitize_html(data)
        elif isinstance(data, dict):
            return {cls.clean_payload(k): cls.clean_payload(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.clean_payload(item) for item in data]
        elif isinstance(data, tuple):
            return tuple(cls.clean_payload(item) for item in data)
        return data

    @classmethod
    def assert_no_command_injection(cls, argument: str) -> str:
        """Verify that a CLI argument contains no unquoted shell metacharacters."""
        if not isinstance(argument, str):
            return argument
        if cls._CMD_DANGEROUS.search(argument):
            raise SecuritySanitizationError(
                f"Potentially dangerous shell metacharacters detected in argument: {argument!r}"
            )
        return argument
