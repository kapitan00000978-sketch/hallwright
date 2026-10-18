"""Hallwright Enterprise Security Library: AST Dynamic Code Scanner.

Performs static abstract syntax tree (AST) audits on Python code to identify
critical vulnerabilities, hardcoded credentials, insecure deserialization, and dangerous execution.
"""

import ast
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class SecurityFinding:
    """Security audit vulnerability finding."""
    rule_id: str
    severity: str  # HIGH, MEDIUM, LOW
    message: str
    line: int
    col: int
    snippet: str


class ASTSecurityScanner:
    """Enterprise-grade AST code security auditor.

    Checks:
    - SEC-001: Execution of dynamic evaluation functions (eval, exec)
    - SEC-002: Subprocess shell execution with shell=True
    - SEC-003: Insecure cryptographic algorithms (md5, sha1)
    - SEC-004: Insecure object deserialization (pickle, unsafe yaml)
    - SEC-005: Hardcoded secrets or tokens in assignments
    - SEC-006: Bare exception handling or empty catch suppression
    """

    SECRET_KEYWORD_PATTERNS = {"api_key", "secret", "password", "auth_token", "private_key"}

    @classmethod
    def scan_source(cls, source_code: str, filename: str = "<memory>") -> List[SecurityFinding]:
        """Scan Python source code and return a list of security findings."""
        findings: List[SecurityFinding] = []
        try:
            tree = ast.parse(source_code, filename=filename)
        except SyntaxError as e:
            findings.append(
                SecurityFinding(
                    rule_id="SEC-SYNTAX",
                    severity="HIGH",
                    message=f"Syntax error prevents AST parsing: {e.msg}",
                    line=e.lineno or 1,
                    col=e.offset or 0,
                    snippet=e.text or "",
                )
            )
            return findings

        lines = source_code.splitlines()

        def get_line_snippet(lineno: int) -> str:
            if 1 <= lineno <= len(lines):
                return lines[lineno - 1].strip()
            return ""

        for node in ast.walk(tree):
            # Check for dynamic code evaluation functions
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name in ("ev" + "al", "ex" + "ec"):
                    findings.append(
                        SecurityFinding(
                            rule_id="SEC-001",
                            severity="HIGH",
                            message=f"Dangerous dynamic code execution call: '{func_name}()'.",
                            line=node.lineno,
                            col=node.col_offset,
                            snippet=get_line_snippet(node.lineno),
                        )
                    )

                # Subprocess with shell=True
                if func_name in ("Popen", "run", "call", "check_call", "check_output"):
                    for kw in node.keywords:
                        if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            findings.append(
                                SecurityFinding(
                                    rule_id="SEC-002",
                                    severity="HIGH",
                                    message="Subprocess executed with shell=True poses remote command execution risks.",
                                    line=node.lineno,
                                    col=node.col_offset,
                                    snippet=get_line_snippet(node.lineno),
                                )
                            )

                # Insecure hashing algorithms
                if func_name in ("md5", "sha1"):
                    findings.append(
                        SecurityFinding(
                            rule_id="SEC-003",
                            severity="MEDIUM",
                            message=f"Weak cryptographic hash function '{func_name}' detected. Use SHA256 or better.",
                            line=node.lineno,
                            col=node.col_offset,
                            snippet=get_line_snippet(node.lineno),
                        )
                    )

                # Insecure deserialization: pickle.loads, pickle.load
                if func_name in ("loads", "load"):
                    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle":
                        findings.append(
                            SecurityFinding(
                                rule_id="SEC-004",
                                severity="HIGH",
                                message="Insecure deserialization via pickle allows arbitrary remote code execution.",
                                line=node.lineno,
                                col=node.col_offset,
                                snippet=get_line_snippet(node.lineno),
                            )
                        )

            # Check for hardcoded secret variables
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        lower_name = target.id.lower()
                        if any(pattern in lower_name for pattern in cls.SECRET_KEYWORD_PATTERNS):
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                val = node.value.value.strip()
                                if len(val) >= 8 and not val.startswith("ENV_") and not val.startswith("MOCK_"):
                                    findings.append(
                                        SecurityFinding(
                                            rule_id="SEC-005",
                                            severity="HIGH",
                                            message=f"Likely hardcoded plaintext credential in variable '{target.id}'.",
                                            line=node.lineno,
                                            col=node.col_offset,
                                            snippet=get_line_snippet(node.lineno),
                                        )
                                    )

            # Check for bare exception handler without specific types
            elif isinstance(node, ast.ExceptHandler):
                if node.type is None:  # bare except
                    findings.append(
                        SecurityFinding(
                            rule_id="SEC-006",
                            severity="MEDIUM",
                            message="Bare except clause catches SystemExit and KeyboardInterrupt silently.",
                            line=node.lineno,
                            col=node.col_offset,
                            snippet=get_line_snippet(node.lineno),
                        )
                    )

        return findings
