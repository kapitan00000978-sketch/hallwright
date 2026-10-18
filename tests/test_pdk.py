"""
Tests for Hallwright Plugin Developer Kit (PDK) and PluginLoader.
Part of Pillar V: Zero-Overhead Plugin & Ecosystem.
"""

import os
import tempfile
import pytest
from src.sdk.pdk import (
    PluginManifest,
    PluginRule,
    PluginContext,
    RuleViolation,
    PluginRegistry,
    sign_manifest,
    verify_manifest_signature,
)
from src.sdk.plugin_loader import PluginLoader


def test_pdk_rule_registration_and_scanning():
    manifest = PluginManifest(
        id="com.example.security-rule",
        name="Example Custom Rules",
        version="1.0.0",
        author="Security Team",
        description="Enforces custom organizational constraints.",
    )

    def forbid_hardcoded_ips(ctx: PluginContext):
        for idx, line in enumerate(ctx.lines, 1):
            if "192.168." in line or "10.0." in line:
                ctx.add_violation(
                    rule_id="SEC-CUSTOM-001",
                    line_number=idx,
                    message="Hardcoded internal IP detected",
                    severity="CRITICAL",
                )

    rule = PluginRule(
        id="SEC-CUSTOM-001",
        name="No Hardcoded IPs",
        category="Security",
        severity="CRITICAL",
        handler=forbid_hardcoded_ips,
    )
    manifest.rules.append(rule)

    registry = PluginRegistry()
    registry.register_plugin(manifest)

    # Test file with violation
    bad_code = "host = '192.168.1.100'\nport = 8080\n"
    violations = registry.scan_file("config.py", bad_code)
    assert len(violations) == 1
    assert violations[0].rule_id == "SEC-CUSTOM-001"
    assert violations[0].line_number == 1
    assert violations[0].severity == "CRITICAL"

    # Test clean file
    clean_code = "host = os.getenv('HOST')\nport = 8080\n"
    violations_clean = registry.scan_file("config.py", clean_code)
    assert len(violations_clean) == 0


def test_cryptographic_manifest_signature():
    secret = "production-ed25519-secret-key-32-bytes"
    manifest = PluginManifest(
        id="com.enterprise.compliance",
        name="Enterprise Compliance Plugin",
        version="2.1.0",
        author="DevSecOps Guild",
    )
    manifest_dict = manifest.to_dict()

    # Sign manifest
    sig = sign_manifest(manifest_dict, secret)
    assert sig is not None
    assert len(sig) == 64  # SHA256 hex string

    manifest_dict["signature"] = sig
    assert verify_manifest_signature(manifest_dict, secret) is True

    # Tamper with version
    manifest_dict["version"] = "2.1.1"
    assert verify_manifest_signature(manifest_dict, secret) is False


def test_plugin_loader_discovery():
    with tempfile.TemporaryDirectory() as temp_dir:
        plugin_file = os.path.join(temp_dir, "my_custom_plugin.py")
        code = (
            "from src.sdk.pdk import PluginManifest, PluginRule\n\n"
            "def check_no_foo(ctx):\n"
            "    for i, line in enumerate(ctx.lines, 1):\n"
            "        if 'foo_bar_forbidden' in line:\n"
            "            ctx.add_violation('CUST-FOO', i, 'Found forbidden pattern')\n\n"
            "MANIFEST = PluginManifest(\n"
            "    id='test.plugin',\n"
            "    name='Test Plugin',\n"
            "    version='1.0.0',\n"
            "    author='Tester',\n"
            "    rules=[PluginRule('CUST-FOO', 'No Foo', 'Style', 'HIGH', check_no_foo)]\n"
            ")\n"
        )
        with open(plugin_file, "w", encoding="utf-8") as f:
            f.write(code)

        loader = PluginLoader(plugins_dir=temp_dir)
        registry = loader.discover_and_load()

        assert "test.plugin" in registry.plugins
        assert len(registry.rules) == 1

        violations = registry.scan_file("sample.py", "x = foo_bar_forbidden + 1\n")
        assert len(violations) == 1
        assert violations[0].rule_id == "CUST-FOO"
