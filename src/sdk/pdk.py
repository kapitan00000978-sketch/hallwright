"""
Hallwright Plugin Developer Kit (PDK)
Zero-dependency SDK for authoring custom gatekeeper rules, domain masters,
and sub-agent extensions with cryptographic signature verification.
Part of Pillar V: Zero-Overhead Plugin & Ecosystem (Bosqich 55-57).
"""

from typing import Callable, Any, Dict, List, Optional
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import os
import time


@dataclass
class RuleViolation:
    rule_id: str
    file_path: str
    line_number: int
    message: str
    severity: str = "HIGH"  # CRITICAL, HIGH, MEDIUM, LOW
    suggestion: Optional[str] = None


@dataclass
class PluginRule:
    id: str
    name: str
    category: str
    severity: str
    handler: Callable[["PluginContext"], List[RuleViolation]]
    description: str = ""


class PluginContext:
    """Context passed to each custom plugin rule during file scanning."""

    def __init__(self, file_path: str, content: str) -> None:
        self.file_path = file_path
        self.content = content
        self.lines = content.splitlines()
        self.violations: List[RuleViolation] = []

    def add_violation(
        self,
        rule_id: str,
        line_number: int,
        message: str,
        severity: str = "HIGH",
        suggestion: Optional[str] = None,
    ) -> None:
        self.violations.append(
            RuleViolation(
                rule_id=rule_id,
                file_path=self.file_path,
                line_number=line_number,
                message=message,
                severity=severity,
                suggestion=suggestion,
            )
        )


@dataclass
class PluginManifest:
    id: str
    name: str
    version: str
    author: str
    description: str = ""
    rules: List[PluginRule] = field(default_factory=list)
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "description": self.description,
            "rules": [
                {
                    "id": r.id,
                    "name": r.name,
                    "category": r.category,
                    "severity": r.severity,
                    "description": r.description,
                }
                for r in self.rules
            ],
            "signature": self.signature,
        }


class PluginRegistry:
    """In-memory registry of loaded plugins and their active inspection rules."""

    def __init__(self) -> None:
        self.plugins: Dict[str, PluginManifest] = {}
        self.rules: List[PluginRule] = []

    def register_plugin(self, manifest: PluginManifest) -> None:
        self.plugins[manifest.id] = manifest
        for rule in manifest.rules:
            if not any(r.id == rule.id for r in self.rules):
                self.rules.append(rule)

    def scan_file(self, file_path: str, content: str) -> List[RuleViolation]:
        ctx = PluginContext(file_path=file_path, content=content)
        for rule in self.rules:
            try:
                rule.handler(ctx)
            except Exception as e:
                ctx.add_violation(
                    rule_id=rule.id,
                    line_number=1,
                    message=f"Plugin rule {rule.id} execution error: {e}",
                    severity="MEDIUM",
                )
        return ctx.violations


# Cryptographic Signature Verification
def sign_manifest(manifest_dict: Dict[str, Any], secret_key: str) -> str:
    """Signs a manifest dictionary deterministically using HMAC-SHA256."""
    data_to_sign = dict(manifest_dict)
    data_to_sign.pop("signature", None)
    canonical = json.dumps(data_to_sign, sort_keys=True, separators=(",", ":"))
    return hmac.new(secret_key.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_manifest_signature(manifest_dict: Dict[str, Any], secret_key: str) -> bool:
    """Verifies that the manifest signature is untampered."""
    sig = manifest_dict.get("signature")
    if not sig:
        return False
    expected_sig = sign_manifest(manifest_dict, secret_key)
    return hmac.compare_digest(sig, expected_sig)
