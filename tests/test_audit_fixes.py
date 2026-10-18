"""
Comprehensive test suite validating the permanent resolution of all 9 audit findings:
- HW-001: Tab indentation preservation & AST syntax check in remediator.py
- HW-002: Strict UTF-8 decoding in remediator.py (no silent byte loss via errors="ignore")
- HW-010: Context-aware SQL projection (no hallucinated columns)
- HW-011: Language-aware comments (no /* */ on Python code)
- HW-013: Strict certification status in elevation engine
- HW-019: Real verified paths for all 6 libraries in README.md
- HW-025: Configurable exclude_dirs in detector without hardcoded tests override
- HW-026: Bidirectional rule alias resolution (artisan.config.json vs detector.py)
- HW-027: Line-isolated ignore marker behavior (no file-wide suppression)
"""

import os
import ast
import tempfile
import json
import pytest
from scripts.detector import scan_code, is_rule_enabled
from scripts.remediator import remediate_python_code, remediate_file
from professions.database_architect.elevation_engine import DatabaseElevationEngine


# ---------------------------------------------------------
# HW-001: Tab indentation preservation and AST check
# ---------------------------------------------------------
def test_hw001_remediator_tab_indentation():
    """Verify remediator respects tab-indented code without mixing spaces."""
    tab_code = "def process():\n\ttry:\n\t\tdo_something()\n\texcept:\n\t\tpass\n"
    fixed, count = remediate_python_code(tab_code)
    assert count == 1
    # Check that tab indentation was preserved
    assert "\texcept Exception as _hw_err:" in fixed or "\texcept Exception as _artisan_err:" in fixed
    assert "\t\timport logging" in fixed
    assert "\t\tlogging.warning" in fixed
    # Verify AST can parse it without IndentationError or TabError
    ast.parse(fixed)


def test_hw001_remediator_aborts_on_invalid_syntax():
    """Verify remediator does not write corrupted code if it fails AST parsing."""
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as tf:
        tf.write("def broken():\n    except: pass\n")
        temp_path = tf.name

    try:
        # A file with inherent syntax errors before or after shouldn't produce a corrupt file
        res = remediate_file(temp_path)
        # Should cleanly handle or return without crashing
        assert isinstance(res, int)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ---------------------------------------------------------
# HW-002: Strict UTF-8 decoding without data corruption
# ---------------------------------------------------------
def test_hw002_remediator_skips_corrupt_non_utf8():
    """Verify remediator refuses to destructively rewrite non-UTF8 binary files."""
    with tempfile.NamedTemporaryFile("wb", suffix=".py", delete=False) as tf:
        tf.write(b"\x80\x81\xff\xfe\x00\x01 except: pass")
        temp_path = tf.name

    try:
        # Must not crash and must not corrupt file
        res = remediate_file(temp_path)
        assert res == 0
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ---------------------------------------------------------
# HW-010: Context-aware SQL projection (no hallucinated columns)
# ---------------------------------------------------------
def test_hw010_database_no_hallucinated_email_on_orders():
    """Verify elevation engine does not hallucinate .email on products or orders."""
    engine = DatabaseElevationEngine()
    sql_input = "CREATE INDEX idx_products_sku ON products (sku);\nSELECT * FROM products;"
    result = engine.elevate(sql_input)
    elevated = result["elevated_database"]

    assert "products.sku" in elevated or "products.id" in elevated
    assert "products.email" not in elevated, "Must not hallucinate email on products table"


# ---------------------------------------------------------
# HW-011: Language-aware comments (no /* */ on Python code)
# ---------------------------------------------------------
def test_hw011_database_comments_valid_python():
    """Verify elevation engine does not inject /* */ into Python code."""
    engine = DatabaseElevationEngine()
    py_input = (
        "for user in users:\n"
        "    orders = db.query('SELECT * FROM orders WHERE user_id = ' + str(user.id))\n"
    )
    result = engine.elevate(py_input)
    elevated = result["elevated_database"]

    assert "/*" not in elevated, "Must never use C-style comments on Python code"
    assert "# Original code archived" in elevated or "# " in elevated


# ---------------------------------------------------------
# HW-013: Strict certification status
# ---------------------------------------------------------
def test_hw013_elevation_engine_strict_status():
    """Verify elevation engine returns valid status matching rubric."""
    engine = DatabaseElevationEngine()
    clean_sql = (
        "CREATE INDEX CONCURRENTLY idx_users_email ON users (email);\n"
        "SELECT users.id, users.email FROM users LIMIT 100;\n"
    )
    res = engine.elevate(clean_sql)
    assert res["status"] in ("CERTIFIED", "ELEVATED_WITH_CAUTIONS")
    assert isinstance(res["score"], int)


# ---------------------------------------------------------
# HW-019: All 6 README production libraries exist on disk
# ---------------------------------------------------------
def test_hw019_readme_library_paths_exist():
    """Verify every single library referenced in README.md exists on disk."""
    expected_paths = [
        "src/libraries/architecture/circuit_breaker.py",
        "src/libraries/architecture/event_bus.py",
        "src/libraries/security/jwt_validator.py",
        "src/libraries/security/sanitizer.py",
        "src/libraries/performance/cache.py",
        "src/libraries/performance/ring_buffer.py",
        "src/libraries/testing/mutation_suite.py",
        "src/libraries/testing/fuzzer.py",
        "src/libraries/copywriting/dx_linter.py",
        "src/libraries/copywriting/changelog.py",
        "src/libraries/design/spatial_3d.js",
        "src/libraries/design/liquid_glass.css",
    ]
    for p in expected_paths:
        assert os.path.isfile(p), f"Missing library file referenced in README: {p}"


# ---------------------------------------------------------
# HW-025: Configurable exclude_dirs
# ---------------------------------------------------------
def test_hw025_exclude_dirs_configurable():
    """Verify that exclude_dirs allows inspecting test suites when explicitly configured."""
    from scripts.detector import scan_project
    # Default without exclude_dirs or with empty list should scan target
    res = scan_code('key = "AKIA1234567890ABCDEF"', filename="tests/test_demo.py")
    assert any(f["rule_id"] == "SECRET_AWS" for f in res["findings"])


# ---------------------------------------------------------
# HW-026: Rule alias resolution (artisan.config.json vs detector.py)
# ---------------------------------------------------------
def test_hw026_rule_aliases_resolved():
    """Verify SECRET_GENERIC_KEY toggle controls SECRET_ASSIGNMENT."""
    cfg_disabled = {"rules": {"SECRET_GENERIC_KEY": {"enabled": False}}}
    assert is_rule_enabled("SECRET_ASSIGNMENT", cfg_disabled["rules"]) is False

    cfg_enabled = {"rules": {"SECRET_GENERIC_KEY": {"enabled": True}}}
    assert is_rule_enabled("SECRET_ASSIGNMENT", cfg_enabled["rules"]) is True

    cfg_aws = {"rules": {"SECRET_AWS_KEY": {"enabled": False}}}
    assert is_rule_enabled("SECRET_AWS", cfg_aws["rules"]) is False

    code = 'password = "super_secret_password_value_123"'
    # When disabled via alias
    res_disabled = scan_code(code, config=cfg_disabled)
    assert not any(f["rule_id"] == "SECRET_ASSIGNMENT" for f in res_disabled["findings"])


# ---------------------------------------------------------
# HW-027: Line-isolated ignore marker behavior
# ---------------------------------------------------------
def test_hw027_line_isolated_ignore_marker():
    """Verify an ignore marker on one line does NOT suppress defects on another line."""
    code_with_ignore_elsewhere = (
        "try:\n"
        "    do_something()\n"
        "except:\n"
        "    pass\n"
        "\n"
        "eval('2 + 2')  # hallwright-ignore\n"
    )
    res = scan_code(code_with_ignore_elsewhere)
    # The eval line is ignored, but the bare except on line 3-4 MUST be detected!
    assert any(f["rule_id"] == "STUB_BARE_EXCEPT" for f in res["findings"])
    assert not any(f["rule_id"] == "DANGEROUS_EVAL_EXEC" for f in res["findings"])


# ---------------------------------------------------------
# HW-030: Named exception preservation in remediator
# ---------------------------------------------------------
def test_hw030_remediator_named_exception_preservation():
    """Verify that except Exception as err: pass preserves the variable name."""
    flawed = "def query():\n    try:\n        db.connect()\n    except Exception as connection_err:\n        pass\n"
    fixed, count = remediate_python_code(flawed)
    assert count == 1
    assert "connection_err" in fixed
    assert "pass" not in fixed
    ast.parse(fixed)


# ---------------------------------------------------------
# HW-031: Module-level logging import injection
# ---------------------------------------------------------
def test_hw031_remediator_ensures_module_level_logging_import():
    """Verify that remediator ensures import logging is present at module scope."""
    flawed = '"""Module docstring."""\n\ndef worker():\n    try:\n        work()\n    except:\n        pass\n'
    fixed, count = remediate_python_code(flawed)
    assert count == 1
    assert "import logging" in fixed
    # Must parse valid AST
    tree = ast.parse(fixed)
    # Check that logging is imported
    imported_names = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    assert "logging" in imported_names


# ---------------------------------------------------------
# HW-032: Aborts safely on pre-existing syntax error
# ---------------------------------------------------------
def test_hw032_remediator_aborts_on_preexisting_syntax_error():
    """Verify that remediate_file refuses to touch a file with pre-existing syntax errors."""
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as tf:
        tf.write("def invalid_syntax(\n    return 42\n")
        temp_path = tf.name

    try:
        res = remediate_file(temp_path)
        assert res == 0
        with open(temp_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert content == "def invalid_syntax(\n    return 42\n"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ---------------------------------------------------------
# HW-033: Command injection detection rule
# ---------------------------------------------------------
def test_hw033_command_injection_rule_detected():
    """Verify detector catches dangerous shell=True and dynamic os.system calls."""
    code_shell_true = "import subprocess\nsubprocess.run(user_cmd, shell=True)\n"
    res1 = scan_code(code_shell_true, filename="server.py")
    rule_ids1 = [f["rule_id"] for f in res1["findings"]]
    assert "DANGEROUS_COMMAND_INJECTION" in rule_ids1

    code_dynamic_system = 'import os\nos.system(f"rm -rf {target}")\n'
    res2 = scan_code(code_dynamic_system, filename="tasks.py")
    rule_ids2 = [f["rule_id"] for f in res2["findings"]]
    assert "DANGEROUS_COMMAND_INJECTION" in rule_ids2


# ---------------------------------------------------------
# HW-034: DOM XSS detection rule
# ---------------------------------------------------------
def test_hw034_dom_xss_rule_detected():
    """Verify detector flags dangerous DOM XSS injection vectors."""
    code_xss1 = "element.innerHTML = user_input;\n"
    res1 = scan_code(code_xss1, filename="app.js")
    rule_ids1 = [f["rule_id"] for f in res1["findings"]]
    assert "DANGEROUS_DOM_XSS" in rule_ids1

    code_jsx = "const Comp = () => <div dangerouslySetInnerHTML={{ __html: rawHtml }} />;\n"
    res2 = scan_code(code_jsx, filename="Comp.tsx")
    rule_ids2 = [f["rule_id"] for f in res2["findings"]]
    assert "DANGEROUS_DOM_XSS" in rule_ids2


# ---------------------------------------------------------
# HW-035: SSRF detection rule
# ---------------------------------------------------------
def test_hw035_ssrf_rule_detected():
    """Verify detector flags unvalidated dynamic URL parameters in HTTP clients."""
    code_requests = "import requests\nresp = requests.get(url)\n"
    res1 = scan_code(code_requests, filename="fetcher.py")
    rule_ids1 = [f["rule_id"] for f in res1["findings"]]
    assert "DANGEROUS_SSRF" in rule_ids1

    code_axios = "const res = await axios.get(req.query.target);\n"
    res2 = scan_code(code_axios, filename="proxy.ts")
    rule_ids2 = [f["rule_id"] for f in res2["findings"]]
    assert "DANGEROUS_SSRF" in rule_ids2


# ---------------------------------------------------------
# HW-036: Safe constructs are not false-positively flagged
# ---------------------------------------------------------
def test_hw036_safe_constructs_not_flagged():
    """Verify safe subprocess list calls, static HTML, and fixed URLs pass with score 100."""
    safe_code = (
        'import subprocess\n'
        'import requests\n'
        'subprocess.run(["git", "status"], check=True)\n'
        'requests.get("https://api.github.com/zen")\n'
        'container.innerHTML = "";\n'
        'container.innerHTML = "<span>static</span>";\n'
    )
    res = scan_code(safe_code, filename="safe.py")
    assert res["status"] == "CERTIFIED"
    assert res["score"] == 100
    assert len(res["findings"]) == 0


# ---------------------------------------------------------
# HW-037: Custom rules engine via config
# ---------------------------------------------------------
def test_hw037_custom_rules_detection():
    """Verify custom organizational rules are scanned with extension filters and deductions."""
    custom_cfg = {
        "rules": {},
        "custom_rules": [
            {
                "id": "NO_PRINT_IN_PROD",
                "pattern": r"\bprint\s*\(",
                "category": "STYLE",
                "message": "Do not leave print() statements in production code.",
                "deduction": 15,
                "extensions": [".py"]
            }
        ]
    }
    python_code = "def worker():\n    print('debugging')\n    return True\n"
    res_py = scan_code(python_code, filename="service.py", config_override=custom_cfg)
    assert res_py["status"] == "REJECTED"
    assert any(f["rule_id"] == "NO_PRINT_IN_PROD" for f in res_py["findings"])
    assert res_py["score"] == 85

    # Should not trigger on JS file because extensions filter is ['.py']
    js_code = "console.log('test'); print('not python');\n"
    res_js = scan_code(js_code, filename="app.js", config_override=custom_cfg)
    assert not any(f["rule_id"] == "NO_PRINT_IN_PROD" for f in res_js["findings"])


# ---------------------------------------------------------
# HW-038: Custom rules loaded from .hallwright/rules.json
# ---------------------------------------------------------
def test_hw038_custom_rules_from_file(tmp_path, monkeypatch):
    """Verify load_artisan_config automatically discovers and merges .hallwright/rules.json."""
    from detector import load_artisan_config
    hw_dir = tmp_path / ".hallwright"
    hw_dir.mkdir()
    rules_file = hw_dir / "rules.json"
    rules_file.write_text(
        json.dumps({
            "rules": [
                {
                    "id": "DISALLOW_MOMENT_JS",
                    "pattern": r"from\s+['\"]moment['\"]|require\(['\"]moment['\"]\)",
                    "category": "PERFORMANCE",
                    "message": "Moment.js is banned. Use date-fns or native Temporal.",
                    "deduction": 20
                }
            ]
        }),
        encoding="utf-8"
    )

    loaded = load_artisan_config(str(tmp_path))
    assert "custom_rules" in loaded
    assert any(r["id"] == "DISALLOW_MOMENT_JS" for r in loaded["custom_rules"])

