"""Tests for Hallwright Domain Code Synthesizer (src/sdk/synthesizer.py).
Verifies zero-stub generation, syntax validity, and domain awareness.
"""

import ast
import os
import sys
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from synthesizer import DomainCodeSynthesizer


def test_detect_domain():
    synth = DomainCodeSynthesizer()
    assert synth.detect_domain("Build JWT authentication and login endpoints") == "auth"
    assert synth.detect_domain("Setup SQLite table migrations and indexed queries") == "database"
    assert synth.detect_domain("Create shopping cart and checkout order processing") == "ecommerce"
    assert synth.detect_domain("Design CSS tokens and responsive dashboard cards") == "ui"
    assert synth.detect_domain("Build REST API route dispatcher") == "api"


def test_synthesize_architecture():
    synth = DomainCodeSynthesizer()
    arch = synth.synthesize_architecture("Build high-throughput payment gateway")
    assert arch["architecture_pattern"] == "Hexagonal / Clean Domain Architecture"
    assert len(arch["components"]) == 3
    assert len(arch["invariants"]) >= 3


def test_synthesize_auth_code_syntax():
    synth = DomainCodeSynthesizer()
    code = synth.synthesize_code("Secure auth service", domain="auth")
    # Must parse cleanly with AST (zero syntax errors)
    parsed = ast.parse(code)
    assert isinstance(parsed, ast.Module)
    assert "class AuthSecurityService:" in code
    assert "def hash_password" in code
    assert "def authenticate_and_issue_token" in code
    assert "TODO" not in code


def test_synthesize_database_code_syntax():
    synth = DomainCodeSynthesizer()
    code = synth.synthesize_code("Customer database manager", domain="database")
    parsed = ast.parse(code)
    assert isinstance(parsed, ast.Module)
    assert "class DatabaseManager:" in code
    assert "def insert_record" in code
    assert "TODO" not in code


def test_synthesize_ecommerce_code_syntax():
    synth = DomainCodeSynthesizer()
    code = synth.synthesize_code("Product shopping cart and checkout", domain="ecommerce")
    parsed = ast.parse(code)
    assert isinstance(parsed, ast.Module)
    assert "class ECommerceService:" in code
    assert "def checkout" in code
    assert "TODO" not in code


def test_synthesize_test_suite():
    synth = DomainCodeSynthesizer()
    test_code = synth.synthesize_test("def hello(): return 'world'", module_name="hello_module")
    parsed = ast.parse(test_code)
    assert isinstance(parsed, ast.Module)
    assert "def test_hello_module_syntax_and_import" in test_code
