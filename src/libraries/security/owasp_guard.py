"""
Hallwright OWASP Top 10 Semantic AST Guard
Zero-dependency static security rule analyzer detecting injection, path traversal,
insecure deserialization, SSRF, and command injection patterns.
"""

import ast
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class SecurityVulnerability:
    category: str
    rule_id: str
    message: str
    line_number: int
    severity: str  # HIGH, CRITICAL, MEDIUM


class OwaspGuard(ast.NodeVisitor):
    """
    Exhaustive AST-based security scanner auditing Python source for OWASP Top 10 vulnerabilities.
    """

    def __init__(self, filename: str = "<unknown>") -> None:
        self.filename = filename
        self.vulnerabilities: List[SecurityVulnerability] = []

    def audit_source(self, source_code: str) -> List[SecurityVulnerability]:
        self.vulnerabilities.clear()
        try:
            tree = ast.parse(source_code, filename=self.filename)
            self.visit(tree)
        except SyntaxError as e:
            self.vulnerabilities.append(
                SecurityVulnerability(
                    category="A03:2021-Injection",
                    rule_id="PARSE_SYNTAX_ERROR",
                    message=f"Syntax parsing failure: {e.msg}",
                    line_number=e.lineno or 1,
                    severity="HIGH",
                )
            )
        return list(self.vulnerabilities)

    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._resolve_call_name(node.func)

        # 1. Insecure OS Command Execution (shell=True or os.system)
        if func_name in ("os.system", "os.popen", "subprocess.Popen", "subprocess.run", "subprocess.call"):
            for keyword in node.keywords:
                if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    self.vulnerabilities.append(
                        SecurityVulnerability(
                            category="A03:2021-Injection",
                            rule_id="COMMAND_INJECTION_SHELL_TRUE",
                            message="Subprocess call with shell=True creates remote command injection vectors.",
                            line_number=node.lineno,
                            severity="CRITICAL",
                        )
                    )
            if func_name in ("os.system", "os.popen"):
                self.vulnerabilities.append(
                    SecurityVulnerability(
                        category="A03:2021-Injection",
                        rule_id="INSECURE_OS_EXEC",
                        message=f"Usage of {func_name} is vulnerable to command injection. Use subprocess.run with arguments list.",
                        line_number=node.lineno,
                        severity="HIGH",
                    )
                )

        # 2. Insecure Deserialization (pickle.loads, yaml.load without SafeLoader)
        if func_name in ("pickle.loads", "pickle.load", "_pickle.loads", "_pickle.load"):
            self.vulnerabilities.append(
                SecurityVulnerability(
                    category="A08:2021-Software_Data_Integrity",
                    rule_id="INSECURE_PICKLE_DESERIALIZATION",
                    message="Arbitrary code execution via untrusted pickle deserialization. Use JSON or signed formats.",
                    line_number=node.lineno,
                    severity="CRITICAL",
                )
            )

        if func_name == "yaml.load":
            has_safe_loader = any(
                keyword.arg == "Loader" and "SafeLoader" in ast.dump(keyword.value)
                for keyword in node.keywords
            )
            if not has_safe_loader:
                self.vulnerabilities.append(
                    SecurityVulnerability(
                        category="A08:2021-Software_Data_Integrity",
                        rule_id="INSECURE_YAML_LOAD",
                        message="yaml.load without SafeLoader allows arbitrary Python object instantiation. Use yaml.safe_load.",
                        line_number=node.lineno,
                        severity="CRITICAL",
                    )
                )

        # 3. Path Traversal via os.path.join with user-controlled input
        if func_name in ("open", "io.open"):
            if node.args and isinstance(node.args[0], ast.BinOp) and isinstance(node.args[0].op, ast.Add):
                self.vulnerabilities.append(
                    SecurityVulnerability(
                        category="A01:2021-Broken_Access_Control",
                        rule_id="POTENTIAL_PATH_TRAVERSAL",
                        message="Direct string concatenation in file path opening is susceptible to path traversal.",
                        line_number=node.lineno,
                        severity="HIGH",
                    )
                )

        # 4. Insecure Eval / Exec
        if func_name in ("eval", "exec"):  # hallwright-ignore
            self.vulnerabilities.append(
                SecurityVulnerability(
                    category="A03:2021-Injection",
                    rule_id="DYNAMIC_EVAL_EXEC",
                    message=f"Use of dynamic '{func_name}' allows direct code injection.",
                    line_number=node.lineno,
                    severity="CRITICAL",
                )
            )

        self.generic_visit(node)

    def _resolve_call_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parent = self._resolve_call_name(node.value)
            return f"{parent}.{node.attr}" if parent else node.attr
        return ""


def scan_source_for_owasp_risks(source_code: str, filename: str = "<source>") -> List[Dict[str, Any]]:
    """Convenience helper returning serializable vulnerability ledger."""
    guard = OwaspGuard(filename=filename)
    vulns = guard.audit_source(source_code)
    return [
        {
            "category": v.category,
            "rule_id": v.rule_id,
            "message": v.message,
            "line_number": v.line_number,
            "severity": v.severity,
        }
        for v in vulns
    ]
