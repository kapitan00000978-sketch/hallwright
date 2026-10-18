"""
Hallwright SQL Injection Neutralizer
Zero-dependency AST analysis tool detecting raw string concatenation, f-strings,
and % format operators inside SQL execution contexts.
"""

import ast
from typing import List, Dict, Any
from dataclasses import dataclass
import re

SQL_VERBS = ("SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE")


@dataclass
class SqlVulnerability:
    file_path: str
    line_number: int
    raw_snippet: str
    risk_level: str  # CRITICAL, HIGH
    explanation: str


class SqlInjectionDetector(ast.NodeVisitor):
    def __init__(self, file_path: str = "<unknown>") -> None:
        self.file_path = file_path
        self.vulnerabilities: List[SqlVulnerability] = []

    def check_source(self, code: str) -> List[SqlVulnerability]:
        self.vulnerabilities.clear()
        try:
            tree = ast.parse(code, filename=self.file_path)
            self.visit(tree)
        except SyntaxError as e:
            self.vulnerabilities.append(
                SqlVulnerability(
                    file_path=self.file_path,
                    line_number=e.lineno or 1,
                    raw_snippet="Syntax parsing error",
                    risk_level="HIGH",
                    explanation=f"SQL AST inspection failed due to syntax error: {e.msg}",
                )
            )
        return list(self.vulnerabilities)

    def visit_Call(self, node: ast.Call) -> None:
        func_name = self._resolve_name(node.func)

        # Check calls named execute, executemany, raw, fetch, etc.
        if func_name.endswith(("execute", "executemany", "raw", "select", "query")):
            if node.args:
                sql_arg = node.args[0]
                self._inspect_sql_argument(sql_arg, node.lineno)

        self.generic_visit(node)

    def _inspect_sql_argument(self, node: ast.AST, lineno: int) -> None:
        # Check f-strings: JoinedStr
        if isinstance(node, ast.JoinedStr):
            # Check if it looks like SQL
            has_sql_verb = False
            for part in node.values:
                if isinstance(part, ast.Constant) and isinstance(part.value, str):
                    if any(verb in part.value.upper() for verb in SQL_VERBS):
                        has_sql_verb = True
                        break
            if has_sql_verb:
                self.vulnerabilities.append(
                    SqlVulnerability(
                        file_path=self.file_path,
                        line_number=lineno,
                        raw_snippet="f-string SQL query execution",
                        risk_level="CRITICAL",
                        explanation="F-string interpolations directly into SQL queries lead to SQL injection. Use parameterized queries (?, %s, or $1).",
                    )
                )

        # Check string concatenation: BinOp Add
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            if self._contains_sql_keyword(node):
                self.vulnerabilities.append(
                    SqlVulnerability(
                        file_path=self.file_path,
                        line_number=lineno,
                        raw_snippet="Concatenated SQL query via + operator",
                        risk_level="CRITICAL",
                        explanation="Dynamic string concatenation inside database queries bypasses parameterized query escaping.",
                    )
                )

        # Check % formatting: BinOp Mod
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
            if self._contains_sql_keyword(node.left):
                self.vulnerabilities.append(
                    SqlVulnerability(
                        file_path=self.file_path,
                        line_number=lineno,
                        raw_snippet="Interpolated SQL query via % operator",
                        risk_level="CRITICAL",
                        explanation="Using Python's % operator on raw SQL strings is insecure. Pass parameters as a separate tuple to execute().",
                    )
                )

    def _contains_sql_keyword(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return any(verb in node.value.upper() for verb in SQL_VERBS)
        if isinstance(node, ast.BinOp):
            return self._contains_sql_keyword(node.left) or self._contains_sql_keyword(node.right)
        return False

    def _resolve_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            parent = self._resolve_name(node.value)
            return f"{parent}.{node.attr}" if parent else node.attr
        return ""


def audit_sql_injections(source_code: str, file_path: str = "<source>") -> List[Dict[str, Any]]:
    detector = SqlInjectionDetector(file_path=file_path)
    vulns = detector.check_source(source_code)
    return [
        {
            "file_path": v.file_path,
            "line_number": v.line_number,
            "raw_snippet": v.raw_snippet,
            "risk_level": v.risk_level,
            "explanation": v.explanation,
        }
        for v in vulns
    ]
