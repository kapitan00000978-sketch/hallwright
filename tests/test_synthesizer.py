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


def test_subtitle_ui_synthesis_domain_adaptation():
    synth = DomainCodeSynthesizer()
    task = "Video subtitr va vaqt taxlash studio interfeysi"
    assert synth.detect_domain(task) == "subtitle"

    html = synth.synthesize_ui_html(task, lang="uz")
    assert "Subtitle Studio Pro" in html
    assert "video-stage-box" in html
    assert "subtitle-overlay" in html
    assert "timeline-scrubber" in html
    assert "btn-shift-plus-100" in html
    assert "cues-container" in html

    js = synth.synthesize_ui_js(task, lang="uz")
    assert "class ApplicationState" in js
    assert "shiftOffset" in js
    assert "exportSRT" in js
    assert "exportVTT" in js
    assert "exportJSON" in js
    # Invariant: Gabriel Frost XSS defense
    assert "innerHTML" not in js


def test_harmonic_color_palette():
    synth = DomainCodeSynthesizer()
    
    # Subtitle Palette: Cinematic Obsidian & Sky/Amber
    sub_css = synth.synthesize_ui_css("Video subtitr taxlash")
    assert "--primary: #0284c7;" in sub_css
    assert "--accent: #f59e0b;" in sub_css
    assert "#07090e" in sub_css
    
    # Ecommerce Palette: Royal Indigo & Emerald
    ecom_css = synth.synthesize_ui_css("Katta savat va onlayn do'kon")
    assert "--primary: #6366f1;" in ecom_css
    assert "--accent: #10b981;" in ecom_css
    
    # Analytics Palette: Cyber Cobalt & Teal
    ana_css = synth.synthesize_ui_css("Monitoring statistika va grafiklar")
    assert "--primary: #2563eb;" in ana_css
    assert "--accent: #0d9488;" in ana_css

    # 3D Palette: Cosmic Obsidian & Quantum Cyan/Nebula Purple
    spatial_css = synth.synthesize_ui_css("Awwwards Three.js WebGL 3D Portal")
    assert "--primary: #00f5ff;" in spatial_css
    assert "--accent: #a855f7;" in spatial_css
    assert "#030712" in spatial_css


def test_detect_domain_3d():
    synth = DomainCodeSynthesizer()
    assert synth.detect_domain("Create Three.js WebGL 3D spatial interactive portal") == "3d"
    assert synth.detect_domain("Awwwards level mesh and PBR shader scene") == "3d"
    assert synth.detect_domain("WebGL canvas3d camera orbitcontrols experience") == "3d"


def test_synthesize_3d_code_syntax():
    synth = DomainCodeSynthesizer()
    code = synth.synthesize_code("Quantum Nexus 3D Three.js experience", domain="3d")
    parsed = ast.parse(code)
    assert isinstance(parsed, ast.Module)
    assert "class ThreeJSSceneBuilder:" in code
    assert "class ThreeJSSceneConfig:" in code
    assert "def export_manifest" in code
    assert "def export_html_bundle" in code
    assert "TorusKnotGeometry" in code
    assert "MeshPhysicalMaterial" in code
    assert "TODO" not in code


def test_threejs_scene_builder_execution():
    synth = DomainCodeSynthesizer()
    code = synth.synthesize_code("Quantum Nexus 3D Three.js experience", domain="3d")
    local_scope = {}
    exec(code, local_scope)
    BuilderClass = local_scope["ThreeJSSceneBuilder"]
    builder = BuilderClass(scene_name="Quantum Realm")
    manifest = builder.export_manifest()

    assert manifest["scene_name"] == "Quantum Realm"
    assert manifest["geometries_count"] >= 1
    assert manifest["lights_count"] >= 3
    assert manifest["particle_systems_count"] >= 1

    html_bundle = builder.export_html_bundle()
    assert "<!DOCTYPE html>" in html_bundle
    assert "three.min.js" in html_bundle
    assert "OrbitControls.js" in html_bundle
    assert "THREE.ACESFilmicToneMapping" in html_bundle
    assert "THREE.MeshPhysicalMaterial" in html_bundle


def test_3d_ui_synthesis_domain_adaptation():
    synth = DomainCodeSynthesizer()
    task = "Awwwards Three.js WebGL Quantum Portal"

    html = synth.synthesize_ui_html(task, lang="uz")
    assert "<!DOCTYPE html>" in html
    assert "three.min.js" in html
    assert "OrbitControls.js" in html
    assert "webgl-canvas" in html
    assert "Awwwards WebGL 2.0" in html
    assert "fps-counter" in html
    assert "material-select" in html

    js = synth.synthesize_ui_js(task, lang="uz")
    assert "THREE.PerspectiveCamera" in js
    assert "THREE.ACESFilmicToneMapping" in js
    assert "THREE.TorusKnotGeometry" in js
    assert "THREE.MeshPhysicalMaterial" in js
    assert "THREE.Raycaster" in js
    assert "requestAnimationFrame" in js
    # Invariant: Gabriel Frost XSS defense
    assert "innerHTML" not in js

    standalone = synth.synthesize_3d_webgl(task, lang="uz")
    assert "<!DOCTYPE html>" in standalone
    assert "<style>" in standalone
    assert "<script>" in standalone
    assert "THREE.WebGLRenderer" in standalone


def test_semantic_chromatic_mood_adaptation():
    synth = DomainCodeSynthesizer()

    # 1. Gold / Luxury
    gold_css = synth.synthesize_ui_css("Hashamatli oltin va qimmatbaho zargarlik buyumlari do'koni")
    assert "--primary: #d4af37;" in gold_css
    assert "--accent: #f59e0b;" in gold_css

    # 2. Crimson / Red / Gaming
    gaming_css = synth.synthesize_ui_css("Esport gaming battle arena with crimson fire")
    assert "--primary: #ef4444;" in gaming_css
    assert "--accent: #f97316;" in gaming_css

    # 3. Emerald / Green / Eco / Fintech
    eco_css = synth.synthesize_ui_css("Yashil tabiat va zumrad eco loyiha portali")
    assert "--primary: #10b981;" in eco_css
    assert "--accent: #06b6d4;" in eco_css

    # 4. Cyberpunk / Neon
    cyber_css = synth.synthesize_ui_css("Cyberpunk neon night arcade simulator")
    assert "--primary: #ff007f;" in cyber_css
    assert "--accent: #00f5ff;" in cyber_css

    # 5. Minimalist Monochrome
    mono_css = synth.synthesize_ui_css("Minimalist monochrome architectural portfolio")
    assert "--primary: #f8fafc;" in mono_css
    assert "--accent: #94a3b8;" in mono_css


def test_synthesize_enterprise_clean_architecture_service():
    synth = DomainCodeSynthesizer()
    code = synth.synthesize_code("Build high-throughput payment order processor with clean architecture and FastAPI", domain="enterprise")
    parsed = ast.parse(code)
    assert isinstance(parsed, ast.Module)
    assert "class DomainError(Exception):" in code
    assert "class EntityNotFoundError" in code
    assert "class DomainValidationError" in code
    assert "class ConcurrencyConflictError" in code
    assert "class IRepository(ABC, Generic[T]):" in code
    assert "class InMemoryRepository" in code
    assert "class EnterpriseDomainService:" in code
    assert "class FastAPIAdapter:" in code

    # Test full execution of the synthesized enterprise service
    local_scope = {}
    exec(code, local_scope)
    AdapterClass = local_scope["FastAPIAdapter"]
    adapter = AdapterClass()

    # 1. Create Record (POST 201)
    res_post = adapter.handle_request("POST", "/records", {"name": "Titanium Order 101"})
    assert res_post["status_code"] == 201
    rec_id = res_post["body"]["id"]

    # 2. Get Record (GET 200)
    res_get = adapter.handle_request("GET", f"/records/{rec_id}")
    assert res_get["status_code"] == 200
    assert res_get["body"]["id"] == rec_id

    # 3. Validation failure (POST 422)
    res_invalid = adapter.handle_request("POST", "/records", {})
    assert res_invalid["status_code"] == 422

    # 4. Not found (GET 404)
    res_not_found = adapter.handle_request("GET", "/records/unknown-id-999")
    assert res_not_found["status_code"] == 404


def test_synthesize_typescript_module():
    synth = DomainCodeSynthesizer()
    ts_code = synth.synthesize_code("TypeScript React Customer Dashboard", filename="CustomerDashboard.tsx")
    assert "export interface DomainEntity" in ts_code
    assert "export type AsyncState<T>" in ts_code
    assert "export class Result<T, E = Error>" in ts_code
    assert "useEntityResource" in ts_code
    assert "AbortController" in ts_code





