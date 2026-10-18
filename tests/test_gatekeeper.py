import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from detector import scan_code, RULES, run_gitleaks

# --- TASK 2: Unit tests for each stub rule ---

def test_stubs_todo():
    res = scan_code("// " + "TODO" + ": implement logic")
    assert res["status"] == "REJECTED"
    assert any("Unfinished stub" in f for f in res["flaws"])

def test_stubs_fixme():
    res = scan_code("# " + "FIXME" + " later: fix edge case")
    assert res["status"] == "REJECTED"
    assert any("Unfinished stub" in f for f in res["flaws"])

def test_stubs_xxx():
    res = scan_code("// " + "XXX" + ": refactor this routine")
    assert res["status"] == "REJECTED"
    assert any("Unfinished stub" in f for f in res["flaws"])

def test_stubs_hack():
    res = scan_code("# " + "HACK" + ": temporary bypass")
    assert res["status"] == "REJECTED"
    assert any("Unfinished stub" in f for f in res["flaws"])

def test_stubs_implement_later():
    res = scan_code("# please " + "implement later")
    assert res["status"] == "REJECTED"
    assert any("Unfinished stub" in f for f in res["flaws"])

def test_stubs_pass_placeholder():
    code = "def handle():\n    pass  # to be filled\n"
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("Pass placeholder" in f for f in res["flaws"])

def test_stubs_empty_catch():
    code1 = "try { run(); } catch (err) {}"
    res1 = scan_code(code1)
    assert res1["status"] == "REJECTED"
    assert any("Empty catch" in f for f in res1["flaws"])

    code2 = "try { run(); } catch {}"
    res2 = scan_code(code2)
    assert res2["status"] == "REJECTED"
    assert any("Empty catch" in f for f in res2["flaws"])

def test_stubs_bare_except():
    code = "try:\n    run()\nexcept:\n    pass\n"
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("Silent exception" in f for f in res["flaws"])

def test_stubs_except_exception_pass():
    code = "try:\n    run()\nexcept Exception:\n    pass\n"
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("Silent exception" in f for f in res["flaws"])


# --- TASK 2: Dangerous Execution ---

def test_dangerous_eval():
    code = "result = eval(user_input)"
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("Dangerous dynamic execution" in f for f in res["flaws"])

def test_dangerous_exec():
    code = "exec(payload)"
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("Dangerous dynamic execution" in f for f in res["flaws"])


# --- TASK 2: Secrets & Credentials ---

def test_secrets_anthropic():
    code = 'key = "sk-ant-api03-abcdefghijklmnopqrstuvwx"'
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("Anthropic API key" in f for f in res["flaws"])

def test_secrets_openai():
    code = 'token = "sk-abcdefghijklmnopqrstuvwxyz1234567890"'
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("API key detected" in f for f in res["flaws"])

def test_secrets_github():
    code1 = 'gh = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"'
    assert scan_code(code1)["status"] == "REJECTED"

    code2 = 'gh = "gho_1234567890abcdefghijklmnopqrstuvwxyz"'
    assert scan_code(code2)["status"] == "REJECTED"

    code3 = 'gh = "github_pat_1234567890abcdefghijklmnopqrstuvwxyz"'
    assert scan_code(code3)["status"] == "REJECTED"

def test_secrets_aws():
    code = 'AWS_KEY = "AKIA1234567890ABCDEF"'
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("AWS Access Key" in f for f in res["flaws"])

def test_secrets_slack():
    code = 'slack = "xoxb-1234567890-abcdefghij"'
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("Slack token" in f for f in res["flaws"])

def test_secrets_google():
    code = 'google_key = "AIza' + 'a' * 35 + '"'
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("Google API key" in f for f in res["flaws"])

def test_secrets_private_key():
    code = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0\n-----END RSA PRIVATE KEY-----"
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("Private Key" in f for f in res["flaws"])

def test_secrets_literal_assignments():
    assert scan_code('password="hunter2"')["status"] == "REJECTED"
    assert scan_code('secret = "super_classified_secret"')["status"] == "REJECTED"
    assert scan_code('api_key = "production_key_xyz"')["status"] == "REJECTED"
    assert scan_code('auth_token: "my-secure-token"')["status"] == "REJECTED"


# --- TASK 2: Inline ignore marker ---

def test_hallwright_ignore_marker():
    code = 'password = "hunter2" # hallwright-ignore\n'
    res = scan_code(code)
    assert res["status"] == "CERTIFIED"
    assert res["score"] == 100
    assert len(res["flaws"]) == 0


# --- TASK 2: Clean code passes ---

def test_clean_sample_passes():
    code = """
def calculate_tax(amount: float, rate: float) -> float:
    \"\"\"Calculates total tax based on the given rate.\"\"\"
    if amount < 0 or rate < 0:
        raise ValueError("Amount and rate must be non-negative")
    return amount * rate
"""
    res = scan_code(code)
    assert res["status"] == "CERTIFIED"
    assert res["score"] == 100
    assert len(res["flaws"]) == 0

def test_dangerous_sql_injection():
    code = 'query = f"SELECT * FROM users WHERE id = {user_id}"'
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("SQL injection" in f for f in res["flaws"])

def test_secrets_jwt():
    # Header.Payload.Signature
    jwt_sample = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4ifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    code = f'token = "{jwt_sample}"'
    res = scan_code(code)
    assert res["status"] == "REJECTED"
    assert any("JWT" in f for f in res["flaws"])

def test_scan_file_exists():
    from detector import scan_file
    res = scan_file("scripts/detector.py")
    assert res is not None
    assert "status" in res

def test_git_hook_installer(tmp_path):
    import importlib.util
    hook_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "install_git_hook.py"))
    spec = importlib.util.spec_from_file_location("install_git_hook", hook_script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Simulated repo with .git directory
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    assert mod.install_hook(target_dir=str(tmp_path), vendor_gate=True) is True

    # Verify gate files were vendored into .hallwright/gate
    gate_dir = tmp_path / ".hallwright" / "gate"
    assert (gate_dir / "detector.py").exists()
    assert (gate_dir / "gatekeeper.py").exists()
    assert (gate_dir / "remediator.py").exists()

    # Verify pre-commit hook invokes vendored gatekeeper
    hook_file = git_dir / "hooks" / "pre-commit"
    assert hook_file.exists()
    content = hook_file.read_text(encoding="utf-8")
    assert ".hallwright/gate/gatekeeper.py" in content

def test_scan_python_ast_eval():
    from detector import scan_python_ast
    code = "def dangerous_function(param):\n    return eval(param)\n"
    findings = scan_python_ast(code, filename="test.py")
    assert len(findings) == 1
    assert findings[0]["rule_id"] == "DANGEROUS_EVAL_EXEC"

def test_scan_python_ast_bare_except():
    from detector import scan_python_ast
    code = "try:\n    perform_action()\nexcept:\n    pass\n"
    findings = scan_python_ast(code, filename="test.py")
    assert len(findings) == 1
    assert findings[0]["rule_id"] == "STUB_BARE_EXCEPT"

def test_remediator_python_bare_except():
    import importlib.util
    rem_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "remediator.py"))
    spec = importlib.util.spec_from_file_location("remediator", rem_script)
    rem = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rem)

    flawed = "try:\n    run()\nexcept:\n    pass\n"
    fixed, count = rem.remediate_python_code(flawed)
    assert count == 1
    assert "logging.warning" in fixed
    assert "pass" not in fixed

def test_remediator_js_empty_catch():
    import importlib.util
    rem_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "remediator.py"))
    spec = importlib.util.spec_from_file_location("remediator", rem_script)
    rem = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rem)

    flawed = "try { execute(); } catch (err) {}"
    fixed, count = rem.remediate_js_code(flawed)
    assert count == 1
    assert "console.error" in fixed

def test_hallwright_config_loader():
    from detector import load_hallwright_config
    cfg = load_hallwright_config(".")
    assert "rules" in cfg
    assert "exclude_dirs" in cfg

def test_hallwright_config_rule_disable():
    from detector import scan_code
    code = "def todo_func():\n    # TODO: implement later\n    pass\n"
    # When enabled (default)
    res_enabled = scan_code(code)
    assert any(f["rule_id"] == "STUB_TODO_FIXME" for f in res_enabled["findings"])

    # When disabled via config override
    custom_cfg = {"rules": {"STUB_TODO_FIXME": {"enabled": False}}}
    res_disabled = scan_code(code, config=custom_cfg)
    assert not any(f["rule_id"] == "STUB_TODO_FIXME" for f in res_disabled["findings"])

def test_benchmark_suite():
    import importlib.util
    bench_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bench", "run_benchmark.py"))
    spec = importlib.util.spec_from_file_location("run_benchmark", bench_file)
    bench_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bench_mod)
    summary = bench_mod.run_benchmark()
    assert summary["total_tasks"] == 10
    assert summary["hallwright_passed"] == 10
    assert summary["total_defects_repaired"] > 0

def test_claude_hook_check_and_heal(tmp_path):
    import importlib.util
    hook_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "claude_hook.py"))
    spec = importlib.util.spec_from_file_location("claude_hook", hook_file)
    hook_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook_mod)

    # Clean file passes
    clean_file = tmp_path / "clean.py"
    clean_file.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    assert hook_mod.check_and_heal(str(clean_file)) is True

    # Auto-remediable file gets healed
    flawed_file = tmp_path / "flawed.py"
    flawed_file.write_text("try:\n    run()\nexcept:\n    pass\n", encoding="utf-8")
    assert hook_mod.check_and_heal(str(flawed_file)) is True
    content = flawed_file.read_text(encoding="utf-8")
    assert "logging.warning" in content


def test_vibe_mode_non_blocking(tmp_path):
    from detector import scan_project
    # Create temporary source file with stub
    src_file = tmp_path / "vibe_example.py"
    src_file.write_text("def quick_prototype():\n    # TODO: refine later\n    return 42\n", encoding="utf-8")
    
    # In strict mode, should fail
    strict_res = scan_project(str(tmp_path), config_override={"mode": "strict", "exclude_dirs": []})
    assert strict_res["passed"] is False
    assert len(strict_res["findings"]) > 0

    # In vibe mode, should pass (non-blocking advisory)
    vibe_res = scan_project(str(tmp_path), config_override={"mode": "vibe", "exclude_dirs": []})
    assert vibe_res["passed"] is True
    assert vibe_res["mode"] == "vibe"
    assert len(vibe_res["findings"]) > 0


def test_council_auditor_attribution():
    # Stub finding should be audited by Marcus Sterling
    res_stub = scan_code("# " + "TODO" + ": implement later")
    assert len(res_stub["findings"]) > 0
    assert "Marcus Sterling" in res_stub["findings"][0]["auditor"]

    # Secret finding should be audited by Gabriel Frost
    fake_key = "sk-ant-" + "a" * 25
    res_secret = scan_code(f'KEY = "{fake_key}"')
    assert len(res_secret["findings"]) > 0
    assert "Gabriel Frost" in res_secret["findings"][0]["auditor"]


def test_multiline_block_stubs():
    # Multiline C/JS-style block comment
    c_code = "/*\n * " + "TODO" + ": finish implementation\n */\nint x = 1;"
    res_c = scan_code(c_code, filename="service.c")
    assert res_c["status"] == "REJECTED"
    assert any("stub" in f.lower() or "todo" in f.lower() for f in res_c["flaws"])

    # Python multiline docstring stub
    py_code = '"""\n' + 'FIXME' + ': optimize algorithm later\n"""\ndef run():\n    return 42\n'
    res_py = scan_code(py_code, filename="service.py")
    assert res_py["status"] == "REJECTED"
    assert any("stub" in f.lower() or "fixme" in f.lower() for f in res_py["flaws"])


def test_secret_assignment_false_positive_suppression():
    # Legitimate test/dummy passwords should NOT be flagged as secret leaks
    dummy_code = 'password = "test123"\napi_key = "dummy"\ntoken = "placeholder"\n'
    res_dummy = scan_code(dummy_code, filename="config.py")
    assert res_dummy["status"] == "CERTIFIED"
    assert res_dummy["score"] == 100

    # Real production-style passwords without dummy keywords MUST be flagged
    real_secret_code = 'password = "prod_98a7x!complex_secret"'
    res_real = scan_code(real_secret_code, filename="config.py")
    assert res_real["status"] == "REJECTED"
    assert any("secret" in f.lower() or "password" in f.lower() for f in res_real["flaws"])


def test_expanded_sql_injection():
    # JS template literal injection
    js_code = "const q = `SELECT * FROM users WHERE id = ${userId}`;"
    res_js = scan_code(js_code, filename="repo.js")
    assert res_js["status"] == "REJECTED"
    assert any("sql" in f.lower() for f in res_js["flaws"])

    # String concatenation SQL injection
    concat_code = 'query = "SELECT * FROM users WHERE id = " + user_id'
    res_concat = scan_code(concat_code, filename="repo.py")
    assert res_concat["status"] == "REJECTED"
    assert any("sql" in f.lower() for f in res_concat["flaws"])

    # Formatted string SQL injection
    fmt_code = 'query = "SELECT * FROM accounts WHERE name = %s" % username'
    res_fmt = scan_code(fmt_code, filename="accounts.py")
    assert res_fmt["status"] == "REJECTED"
    assert any("sql" in f.lower() for f in res_fmt["flaws"])


def test_graduated_multi_file_scoring(tmp_path):
    from detector import scan_project
    # Create 5 clean files
    for i in range(4):
        f = tmp_path / f"clean_{i}.py"
        f.write_text(f"def func_{i}():\n    return {i}\n", encoding="utf-8")
    # Create 1 file with a minor stub (deduction: 20)
    flawed = tmp_path / "flawed.py"
    flawed.write_text("def stub_func():\n    # " + "TODO" + ": implement\n    return None\n", encoding="utf-8")

    # In previous flawed scoring: (100 - 20) = 80 if 1 file, but if 5 files had deductions total was summed.
    # Now: 4 files with score 100, 1 file with score 80 -> Average project score = (400 + 80)/5 = 96
    res = scan_project(str(tmp_path), config_override={"mode": "vibe", "exclude_dirs": []})
    assert res["score"] == 96
    assert res["metrics"]["warning_count"] == 1
    assert res["metrics"]["critical_count"] == 0


def test_gatekeeper_auto_heal_pass(tmp_path, monkeypatch):
    import importlib.util
    gk_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts", "pre-commit-gatekeeper.py"))
    spec = importlib.util.spec_from_file_location("gatekeeper", gk_path)
    gk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gk)

    # Create a file with an empty exception block
    test_file = tmp_path / "flawed_service.py"
    test_file.write_text("def run():\n    try:\n        do_work()\n    except:\n        pass\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    # First: without heal, it fails
    assert gk.scan_files(staged_only=False, vibe_override=False, heal=False) is False

    # Second: with heal, it auto-repairs the file and passes
    assert gk.scan_files(staged_only=False, vibe_override=False, heal=True) is True
    repaired_code = test_file.read_text(encoding="utf-8")
    assert "import logging" in repaired_code
    assert "pass" not in repaired_code





