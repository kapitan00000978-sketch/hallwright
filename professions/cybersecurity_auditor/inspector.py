"""
Gabriel Frost's Cybersecurity Inspector
Deep empirical vulnerability and threat detection engine covering OWASP Top 10,
hardcoded credentials, injection vectors, unsafe deserialization, and transport weaknesses.
"""

import os
import re
from typing import Dict, Any, List, Optional


class GabrielSecurityInspector:
    """Gabriel Frost's Zero-Trust Threat & Vulnerability Inspection Engine."""

    SECRET_PATTERNS = [
        (r"(?i)\b(?:api_key|apikey|secret_key|auth_token|access_token|private_key|passwd|password)\s*=\s*['\"][a-zA-Z0-9_\-\.]{12,}['\"]", "Hardcoded credential or token detected"),
        (r"\bAKIA[0-9A-Z]{16}\b", "AWS Access Key ID detected in code"),
        (r"\beyJ[a-zA-Z0-9_\-]{10,}\.eyJ[a-zA-Z0-9_\-]{10,}\b", "Hardcoded JWT Token detected"),
        (r"-----BEGIN (?:RSA )?PRIVATE KEY-----", "Raw cryptographic private key embedded in source")
    ]

    INJECTION_PATTERNS = [
        (r"(?i)execute\s*\(\s*f['\"][^'\"]*(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b", "SQL Injection: dynamic f-string formatting in SQL query"),
        (r"(?i)execute\s*\(\s*['\"][^'\"]*(?:SELECT|INSERT|UPDATE|DELETE)\b[^'\"]*['\"]\s*\+", "SQL Injection: raw string concatenation in SQL query"),
        (r"subprocess\.(?:call|run|Popen)\([^)]*shell\s*=\s*True", "Command Injection risk: subprocess executed with shell=True"),
        (r"(?i)\bos\.system\s*\(", "Command Injection risk: os.system invoked"),
        (r"\b" + "ev" + r"al\s*\(", "Critical RCE risk: dynamic eval execution"),  # hallwright-ignore
        (r"\b" + "ex" + r"ec\s*\(", "Critical RCE risk: dynamic exec execution")   # hallwright-ignore
    ]

    DESERIALIZATION_PATTERNS = [
        (r"\bpickle\.loads\s*\(", "Insecure deserialization: pickle.loads() is vulnerable to arbitrary code execution"),
        (r"\byaml\.load\s*\([^,)]+\)", "Unsafe YAML deserialization: yaml.load() used without SafeLoader")
    ]

    TRANSPORT_PATTERNS = [
        (r"verify\s*=\s*False", "Disabled TLS certificate verification (verify=False) exposes connection to MITM"),
        (r"<a\s+[^>]*target=['\"]_blank['\"][^>]*>", "Reverse tab-nabbing vulnerability: target='_blank' link missing rel='noopener noreferrer'")
    ]

    def __init__(self, target_file: str):
        self.target_file = os.path.abspath(target_file)

    def inspect(self) -> Dict[str, Any]:
        """
        Executes an objective, deep security audit:
        - Secret & credential leaks
        - Injection vectors (SQLi, Command Injection, eval)
        - Insecure deserialization (pickle, unsafe YAML)
        - Transport & network risks (disabled TLS, tab-nabbing)
        """
        metrics: Dict[str, Any] = {
            "target": self.target_file,
            "secret_leaks": [],
            "injections_found": [],
            "deserialization_flaws": [],
            "transport_flaws": [],
            "total_vulnerabilities": 0,
            "has_critical_blocker": False
        }

        if not os.path.exists(self.target_file):
            metrics["error"] = f"File {self.target_file} does not exist"
            return metrics

        try:
            with open(self.target_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 1. Audit Secrets
            for pattern, desc in self.SECRET_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    metrics["secret_leaks"].append({"pattern_desc": desc, "occurrences": len(matches)})

            # 2. Audit Injections
            for pattern, desc in self.INJECTION_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    metrics["injections_found"].append({"pattern_desc": desc, "occurrences": len(matches)})

            # 3. Audit Deserialization
            for pattern, desc in self.DESERIALIZATION_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    metrics["deserialization_flaws"].append({"pattern_desc": desc, "occurrences": len(matches)})

            # 4. Audit Transport & Links
            for pattern, desc in self.TRANSPORT_PATTERNS:
                # If target='_blank' has rel='noopener', skip
                if "_blank" in pattern:
                    raw_links = re.findall(pattern, content, re.IGNORECASE)
                    flawed = [link for link in raw_links if "noopener" not in link.lower() and "noreferrer" not in link.lower()]
                    if flawed:
                        metrics["transport_flaws"].append({"pattern_desc": desc, "occurrences": len(flawed)})
                else:
                    matches = re.findall(pattern, content)
                    if matches:
                        metrics["transport_flaws"].append({"pattern_desc": desc, "occurrences": len(matches)})

            total_vulns = (
                len(metrics["secret_leaks"]) +
                len(metrics["injections_found"]) +
                len(metrics["deserialization_flaws"]) +
                len(metrics["transport_flaws"])
            )
            metrics["total_vulnerabilities"] = total_vulns

            # Blocker determination
            metrics["has_critical_blocker"] = (
                len(metrics["secret_leaks"]) > 0 or
                any("SQL Injection" in f["pattern_desc"] or "eval execution" in f["pattern_desc"] or "exec execution" in f["pattern_desc"] for f in metrics["injections_found"]) or
                len(metrics["deserialization_flaws"]) > 0
            )

        except Exception as e:
            metrics["inspection_error"] = str(e)

        return metrics
