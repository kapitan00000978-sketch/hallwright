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


def test_synthesize_ui_assets():
    synth = DomainCodeSynthesizer()
    css = synth.synthesize_ui_css("Katta Boshqaruv Markazi", lang="uz")
    assert "--bg-main" in css
    assert "backdrop-filter" in css
    assert "Elena Rostova" in css

    html = synth.synthesize_ui_html("Katta Boshqaruv Markazi", lang="uz")
    assert "<!DOCTYPE html>" in html
    assert "Katta Boshqaruv Markazi" in html
    assert "app.js" in html

    js = synth.synthesize_ui_js("Katta Boshqaruv Markazi", lang="uz")
    assert "class ApplicationState" in js
    assert "triggerAudit" in js


def test_auth_service_execution():
    synth = DomainCodeSynthesizer()
    code = synth.synthesize_code("Secure auth service", domain="auth")
    local_scope = {}
    exec(code, local_scope)
    AuthClass = local_scope["AuthSecurityService"]
    auth = AuthClass()

    user = auth.register_user("superadmin", "strong_password_123", role="admin")
    assert user["role"] == "admin"

    token_info = auth.authenticate_and_issue_token("superadmin", "strong_password_123")
    token = token_info["access_token"]
    assert auth.check_permission(token, "user") is True
    assert auth.check_permission(token, "admin") is True


def test_database_manager_execution():
    synth = DomainCodeSynthesizer()
    code = synth.synthesize_code("Database service", domain="database")
    local_scope = {}
    exec(code, local_scope)
    DBClass = local_scope["DatabaseManager"]
    db = DBClass(db_path=":memory:")

    db.insert_record("item1", "val1", category="general")
    rec = db.get_record("item1")
    assert rec["value"] == "val1"
    assert db.count_records() == 1

    db.delete_record("item1", soft=True)
    assert db.get_record("item1") is None
    assert db.count_records() == 0


def test_ecommerce_service_execution():
    synth = DomainCodeSynthesizer()
    code = synth.synthesize_code("Store service", domain="ecommerce")
    local_scope = {}
    exec(code, local_scope)
    StoreClass = local_scope["ECommerceService"]
    store = StoreClass()

    store.add_product("p1", "Smart Soat", 100.0, 10)
    order = store.checkout("cust_1", [{"product_id": "p1", "quantity": 2}], coupon_code="CHEMPION10")
    assert order["status"] == "CONFIRMED"
    assert len(order["items"]) == 1
    assert store.catalog["p1"].inventory == 8


def test_ecommerce_ui_synthesis_domain_adaptation():
    synth = DomainCodeSynthesizer()
    task = "Zamonaviy Online Do'kon va Savat Tizimi"
    assert synth.detect_domain(task) == "ecommerce"

    html = synth.synthesize_ui_html(task, lang="uz")
    assert "Smart Bazar" in html
    assert "product-grid" in html
    assert "cart-modal" in html
    assert "checkout-modal" in html
    assert "CHEMPION10" in html

    js = synth.synthesize_ui_js(task, lang="uz")
    assert "class ApplicationState" in js
    assert "addToCart" in js
    assert "applyCoupon" in js
    assert "formatPrice" in js
    # Invariant: Must NOT use innerHTML (Gabriel Frost XSS defense)
    assert "innerHTML" not in js


def test_analytics_ui_synthesis_domain_adaptation():
    synth = DomainCodeSynthesizer()
    task = "Korporativ Sotuvlar Statistikasi va Tahlil Paneli"
    assert synth.detect_domain(task) == "analytics"

    html = synth.synthesize_ui_html(task, lang="uz")
    assert "Analytics Intelligence" in html
    assert "chart-bars-wrap" in html
    assert "data-table" in html

    js = synth.synthesize_ui_js(task, lang="uz")
    assert "class ApplicationState" in js
    assert "periodData" in js
    assert "renderTransactions" in js


