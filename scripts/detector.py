#!/usr/bin/env python3
"""
Hallwright Quality & Security Detection Engine
Shared rule-based detector for pre-commit gatekeeper, live watchdog, and MCP server.
Supports full repository auditing, staged git diff scanning, and single-file inspections.
"""

import os
import sys
import re
import json
import shutil
import argparse
import subprocess
from typing import List, Dict, Any, Optional

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

IGNORE_MARKER = "artisan-ignore"
IGNORE_MARKERS = ("artisan-ignore", "hallwright-ignore")

def is_ignored(text: str) -> bool:
    return any(marker in text for marker in IGNORE_MARKERS)

# Safe placeholder values that should NOT trigger false-positive secret alerts
DUMMY_SECRET_VALUES = {
    "test", "testing", "test123", "dummy", "placeholder", "changeme",
    "example", "sample", "temp", "fake", "dev", "local", "mock",
    "none", "null", "undefined", "default", "localhost", "admin", "secret",
    "password", "passwd", "123456", "qwerty", "your_key_here", "your_api_key",
    "testpass", "test_password", "test_secret", "dummy_token", "xxx", "foo", "bar"
}

# Rule Definitions: (id, category, regex_pattern, message, score_deduction)
RULES = [
    # 1. Stubs & Placeholders (hallwright-ignore)
    (
        "STUB_TODO_FIXME",
        "STUB",
        r"(?:#|//|/\*|--|\*)\s*.*?\b(?:todo|fixme|xxx|hack|tbd|stub:)\b|\bimplement\s+later\b",  # hallwright-ignore
        "Unfinished stub or placeholder detected. Complete all logic end-to-end.",
        20
    ),
    (
        "STUB_PASS_PLACEHOLDER",
        "STUB",
        r"\bpass\s*#.*",  # hallwright-ignore
        "Pass placeholder detected. Implement complete functionality.",
        20
    ),
    (
        "STUB_EMPTY_CATCH",
        "STUB",
        r"catch\s*(?:\([^)]*\))?\s*\{\s*\}",  # hallwright-ignore
        "Empty catch block detected. Handle or log exceptions properly.",
        25
    ),
    (
        "STUB_BARE_EXCEPT",
        "STUB",
        r"except(?:\s+Exception(?:\s+as\s+[a-zA-Z0-9_]+)?)?\s*:\s*pass\b|except\s*:\s*pass\b",  # hallwright-ignore
        "Silent exception suppression detected. Log or handle errors.",  # hallwright-ignore
        25
    ),

    # 2. Dangerous Dynamic Execution & Injections (hallwright-ignore)
    (
        "DANGEROUS_EVAL_EXEC",
        "DANGEROUS",
        r"\b(?:eval|exec)\s*\(",  # hallwright-ignore
        "Dangerous dynamic execution ('eval' or 'exec') detected. Replace with safe structured parsing.",
        30
    ),
    (
        "DANGEROUS_SQL_INJECTION",
        "DANGEROUS",
        r"""(?i)(?:\bf["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM|DROP\s+(?:TABLE|DATABASE|VIEW))\s+.*\{|`.*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM|DROP\s+(?:TABLE|DATABASE|VIEW))\s+.*?\$\{|\b(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM)\s+[^"'\r\n]*["']\s*\+\s*[a-zA-Z_]|[a-zA-Z_]\s*\+\s*["'][^"'\r\n]*(?:WHERE|AND|OR|FROM)\s+|["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM)\s+.*\{\}\s*["']\.format\s*\(|(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM)\s+.*?(?:%s|%d|%v)\s*["']\s*%(?!\s*["'])|fmt\.Sprintf\s*\(\s*["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM)|String\.format\s*\(\s*["'].*?(?:SELECT\s+.*?\bFROM|INSERT\s+INTO|UPDATE\s+.*?\bSET|DELETE\s+FROM))""",
        "Potential SQL injection via raw string interpolation or concatenation. Use parameterized queries.",
        30
    ),
    (
        "DANGEROUS_COMMAND_INJECTION",
        "DANGEROUS",
        r"""(?:\b(?:subprocess\.(?:Popen|run|call|check_call|check_output))\s*\([^)]*?\bshell\s*=\s*True|\bos\.system\s*\(\s*(?:f["'][^"']*\{|["'][^"']*["']\s*\+|[a-zA-Z_]\w*))""",
        "Dangerous dynamic shell execution or command injection risk detected ('shell=True' or dynamic 'os.system'). Use subprocess.run with argument sequence.",
        30
    ),
    (
        "DANGEROUS_DOM_XSS",
        "DANGEROUS",
        r"""(?i)(?:\bdangerouslySetInnerHTML\s*=\s*\{\s*\{?\s*__html\s*:|(?<![a-zA-Z0-9_])innerHTML\s*=\s*(?:`[^`]*\$\{[^}]+\}[^`]*`|["'][^"']*["']\s*\+\s*[a-zA-Z0-9_]|[a-zA-Z0-9_]\w*\s*\+\s*["']|(?!\s*["'`])(?!\s*null\b)(?!\s*undefined\b)[a-zA-Z_$][a-zA-Z0-9_$.]*\s*(?:;|$|\)|,)))""",
        "Potential DOM Cross-Site Scripting (XSS) sink detected. Sanitize dynamic content or use textContent/safe templating.",
        25
    ),
    (
        "DANGEROUS_SSRF",
        "DANGEROUS",
        r"""(?i)\b(?:requests\.(?:get|post|put|delete|patch)|urllib\.request\.urlopen|axios\.(?:get|post|put|delete))\s*\(\s*(?:url|req\.query|req\.params|user_input|target_url|input_url)\b""",
        "Potential Server-Side Request Forgery (SSRF) via unvalidated dynamic URL parameter. Validate URL against allowlist.",
        25
    ),

    # 3. Secrets & Sensitive Credentials (artisan-ignore)
    (
        "SECRET_ANTHROPIC",
        "SECRET",
        r"sk-ant-[a-zA-Z0-9_\-]{20,}",
        "Anthropic API key detected. Externalize credentials via environment variables.",
        35
    ),
    (
        "SECRET_OPENAI",
        "SECRET",
        r"sk-[a-zA-Z0-9_\-]{20,}",
        "OpenAI API key detected. Externalize credentials via environment variables.",
        35
    ),
    (
        "SECRET_GITHUB",
        "SECRET",
        r"(?:ghp|gho|github_pat)_[a-zA-Z0-9_]{20,}",
        "GitHub token detected. Externalize credentials via environment variables.",
        35
    ),
    (
        "SECRET_AWS",
        "SECRET",
        r"AKIA[0-9A-Z]{16}",
        "AWS Access Key ID detected. Externalize credentials via environment variables.",
        35
    ),
    (
        "SECRET_SLACK",
        "SECRET",
        r"xox[baprs]-[0-9a-zA-Z_\-]{10,}",
        "Slack token detected. Externalize credentials via environment variables.",
        35
    ),
    (
        "SECRET_GOOGLE",
        "SECRET",
        r"AIza[0-9A-Za-z_\-]{35}",
        "Google API key detected. Externalize credentials via environment variables.",
        35
    ),
    (
        "SECRET_PRIVATE_KEY",
        "SECRET",
        r"-----BEGIN [A-Z0-9_\- ]*PRIVATE KEY-----",
        "Plaintext Private Key block detected. Externalize secrets securely.",
        35
    ),
    (
        "SECRET_JWT",
        "SECRET",
        r"eyJ[a-zA-Z0-9_\-]{15,}\.eyJ[a-zA-Z0-9_\-]{15,}\.[a-zA-Z0-9_\-]{10,}",
        "Hardcoded JSON Web Token (JWT) detected. Externalize tokens securely.",
        35
    ),
    (
        "SECRET_ASSIGNMENT",
        "SECRET",
        r"""\b(?:[a-zA-Z0-9_]*_)?(?:password|passwd|pwd|secret|token|api_key|apikey|auth_token)\s*[:=]\s*["']([^"'\r\n]{4,})["']""",
        "Hardcoded password, secret, or API token assignment detected. Use environment variables.",
        35
    ),
]

# Pre-compiled rules using re.IGNORECASE
COMPILED_RULES = [
    (r[0], r[1], re.compile(r[2], re.IGNORECASE), r[3], r[4])
    for r in RULES
]

# Compatibility alias for scripts expecting PATTERNS tuple format
PATTERNS = [(r[2], r[0], r[3]) for r in RULES]

# Rule ID aliases to guarantee config compatibility (HW-026)
RULE_ALIASES = {
    "SECRET_ANTHROPIC_KEY": "SECRET_ANTHROPIC",
    "SECRET_OPENAI_KEY": "SECRET_OPENAI",
    "SECRET_AWS_KEY": "SECRET_AWS",
    "SECRET_GENERIC_KEY": "SECRET_ASSIGNMENT",
    "SECRET_ASSIGNMENT": "SECRET_GENERIC_KEY",
    "SECRET_ANTHROPIC": "SECRET_ANTHROPIC_KEY",
    "SECRET_OPENAI": "SECRET_OPENAI_KEY",
    "SECRET_AWS": "SECRET_AWS_KEY",
}

def is_rule_enabled(rule_id: str, rules_cfg: Dict[str, Any]) -> bool:
    """Checks whether a rule is enabled in configuration, resolving any alias names (HW-026)."""
    if rule_id in rules_cfg:
        return rules_cfg[rule_id].get("enabled", True)
    alt = RULE_ALIASES.get(rule_id)
    if alt and alt in rules_cfg:
        return rules_cfg[alt].get("enabled", True)
    return True

# Council of Masters domain ownership
COUNCIL_AUDITORS = {
    "STUB": "Marcus Sterling (Senior Architect)",
    "SECRET": "Gabriel Frost (Cybersecurity Auditor)",
    "DANGEROUS": "Gabriel Frost & Arthur Pendelton",
    "AST": "Marcus Sterling & Dr. Evelyn Reed",
    "DESIGN": "Elena 'The Visionary' Rostova (Design & Spatial Systems)",
}


def run_gitleaks(target_dir: str = ".") -> List[Dict[str, Any]]:
    """Run gitleaks if installed, otherwise return empty list."""
    gitleaks_bin = shutil.which("gitleaks")
    if not gitleaks_bin:
        return []

    try:
        proc = subprocess.run(
            [gitleaks_bin, "detect", "--no-git", "--source", target_dir, "--report-format", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15
        )
        if proc.returncode != 0 and proc.stdout:
            leaks = json.loads(proc.stdout)
            findings = []
            for item in leaks:
                findings.append({
                    "rule_id": "GITLEAKS_" + item.get("RuleID", "LEAK"),
                    "category": "SECRET",
                    "file": item.get("File", ""),
                    "line": item.get("StartLine", 0),
                    "message": f"gitleaks: {item.get('Description', 'Exposed Secret')}",
                    "deduction": 35
                })
            return findings
    except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError, OSError):
        return []
    return []


def scan_python_ast(code: str, filename: str = "") -> List[Dict[str, Any]]:
    """Performs deep Abstract Syntax Tree (AST) analysis on Python code."""
    import ast
    ast_findings: List[Dict[str, Any]] = []
    try:
        tree = ast.parse(code, filename=filename or "<input>")
    except (SyntaxError, ValueError):
        return []

    lines = code.splitlines()

    for node in ast.walk(tree):
        # 1. Detect dynamic eval/exec
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in ("eval", "exec"):
                line_no = getattr(node, "lineno", 1)
                line_content = lines[line_no - 1] if line_no <= len(lines) else ""
                if not is_ignored(line_content):
                    ast_findings.append({
                        "rule_id": "DANGEROUS_EVAL_EXEC",
                        "category": "DANGEROUS",
                        "auditor": COUNCIL_AUDITORS["DANGEROUS"],
                        "file": filename,
                        "line": line_no,
                        "matched_text": f"{func.id}(...)",
                        "message": f"Dangerous dynamic execution ('{func.id}') verified via AST analysis.",
                        "deduction": 30
                    })
        # 2. Detect empty except blocks in AST
        elif isinstance(node, ast.ExceptHandler):
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                line_no = getattr(node, "lineno", 1)
                line_content = lines[line_no - 1] if line_no <= len(lines) else ""
                if not is_ignored(line_content):
                    exc_name = "bare except" if node.type is None else "except"
                    ast_findings.append({
                        "rule_id": "STUB_BARE_EXCEPT",
                        "category": "STUB",
                        "auditor": COUNCIL_AUDITORS["STUB"],
                        "file": filename,
                        "line": line_no,
                        "matched_text": f"except {exc_name}: pass",
                        "message": f"Silent exception suppression ('except {exc_name}: pass') verified via AST.",
                        "deduction": 25
                    })
    return ast_findings


def load_artisan_config(base_dir: str = ".") -> Dict[str, Any]:
    """Loads hallwright.config.json or artisan.config.json and .hallwright/rules.json, returning merged config."""
    config: Dict[str, Any] = {}
    for cfg_name in ["hallwright.config.json", "artisan.config.json"]:
        config_path = os.path.join(base_dir, cfg_name)
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    break
            except (OSError, json.JSONDecodeError):
                continue

    # Also look for .hallwright/rules.json for custom organizational rules
    rules_json_path = os.path.join(base_dir, ".hallwright", "rules.json")
    if os.path.exists(rules_json_path):
        try:
            with open(rules_json_path, "r", encoding="utf-8") as f:
                rules_data = json.load(f)
                custom_rules = rules_data.get("rules", rules_data if isinstance(rules_data, list) else [])
                if custom_rules and isinstance(custom_rules, list):
                    config.setdefault("custom_rules", []).extend(custom_rules)
        except Exception as _hw_err:
            import logging
            logging.warning(f'Handled error: {_hw_err}')  # hallwright-ignore

    return config

load_hallwright_config = load_artisan_config


def scan_multilingual_structural(code: str, filename: str = "") -> List[Dict[str, Any]]:
    """
    Lightweight AST-like structural analysis for JavaScript, TypeScript, Go, Java, and C#.
    Detects multiline empty catches, unparameterized SQL, and DOM XSS sinks.
    """
    findings: List[Dict[str, Any]] = []
    norm_fn = filename.lower().replace("\\", "/")

    # JS/TS structural check
    if norm_fn.endswith((".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")):
        # Multiline empty catch: catch (...) { \n }
        for m in re.finditer(r"catch\s*(?:\([^)]*\))?\s*\{\s*\}", code):
            start_pos = m.start()
            line_no = code[:start_pos].count("\n") + 1
            line_str = code.splitlines()[line_no - 1] if line_no <= len(code.splitlines()) else ""
            if not is_ignored(line_str):
                findings.append({
                    "rule_id": "STUB_EMPTY_CATCH",
                    "category": "STUB",
                    "auditor": COUNCIL_AUDITORS["STUB"],
                    "file": filename,
                    "line": line_no,
                    "matched_text": m.group(0),
                    "message": "Empty JS/TS catch block detected. Handle or log exceptions properly.",
                    "deduction": 25
                })

    # Java/C# structural check
    elif norm_fn.endswith((".java", ".cs")):
        for m in re.finditer(r"catch\s*\([^\)]*Exception[^\)]*\)\s*\{\s*\}", code):
            start_pos = m.start()
            line_no = code[:start_pos].count("\n") + 1
            line_str = code.splitlines()[line_no - 1] if line_no <= len(code.splitlines()) else ""
            if not is_ignored(line_str):
                findings.append({
                    "rule_id": "STUB_EMPTY_CATCH",
                    "category": "STUB",
                    "auditor": COUNCIL_AUDITORS["STUB"],
                    "file": filename,
                    "line": line_no,
                    "matched_text": m.group(0),
                    "message": "Empty Java/C# catch block detected. Log or handle exceptions properly.",
                    "deduction": 25
                })

    return findings


def scan_ui_design_standards(code: str, filename: str = "") -> List[Dict[str, Any]]:
    """
    Elena Rostova UI/UX Craftsmanship & Anti-Generic Guardrail.
    Protects AI agents from generating flat, dead, low-contrast, or unstyled designs:
    - Rejects flat pitch-black voids without atmospheric lighting/depth
    - Flags generic default browser fonts (Arial / Times New Roman) without modern typography stack
    - Enforces responsive viewport meta tags in HTML documents
    """
    findings: List[Dict[str, Any]] = []
    norm_fn = filename.lower().replace("\\", "/")
    
    # Exclude vendor and node_modules
    if any(p in norm_fn for p in ["/.vendor/", "/node_modules/", "vision_proof", "hallwright_demo"]):
        return []
    if norm_fn.endswith(".py") and "/tests/" in norm_fn:
        return []

    # Target only UI files (HTML, CSS, Vue, Svelte) or in-memory HTML scans
    is_ui_file = norm_fn.endswith((".html", ".htm", ".vue", ".svelte", ".css"))
    if not (is_ui_file or (not filename and "<html" in code)):
        return []

    lines = code.splitlines()

    # 1. Reject flat pitch-black void with zero atmospheric lighting
    has_black_void = bool(re.search(r"""(?i)(?:class=["'][^"']*\bbg-black\b|background(?:-color)?\s*:\s*(?:#000(?:000)?|black|#050505|#08090d)\b)""", code))
    has_atmospheric_depth = bool(re.search(r"""(?i)(?:radial-gradient|linear-gradient|conic-gradient|ambient-glow|ambient-mesh|stars-canvas|<canvas\b|backdrop-filter|box-shadow\s*:\s*0\s+0|border-beam)""", code))

    if has_black_void and not has_atmospheric_depth:
        for idx, line in enumerate(lines, 1):
            if re.search(r"""(?i)(?:\bbg-black\b|background(?:-color)?\s*:\s*(?:#000|black|#050505|#08090d))""", line):
                if not is_ignored(line):
                    findings.append({
                        "rule_id": "DESIGN_FLAT_PITCH_BLACK_VOID",
                        "category": "DESIGN",
                        "auditor": COUNCIL_AUDITORS.get("DESIGN", "Elena 'The Visionary' Rostova"),
                        "file": filename,
                        "line": idx,
                        "matched_text": line.strip()[:60],
                        "message": "Flat pitch-black void detected with zero atmospheric lighting. Elena Rostova Invariant: Enforce layered ambient mesh or cosmic depth tokens.",
                        "deduction": 20
                    })
                break

    # 2. Flag generic default browser fonts without modern typography stack
    generic_font_pattern = r"""(?i)font-family\s*:\s*['"]?(?:Arial|Times New Roman|Courier New|Verdana)['"]?\s*;"""
    for idx, line in enumerate(lines, 1):
        if re.search(generic_font_pattern, line):
            if not is_ignored(line):
                findings.append({
                    "rule_id": "DESIGN_GENERIC_FONT",
                    "category": "DESIGN",
                    "auditor": COUNCIL_AUDITORS.get("DESIGN", "Elena 'The Visionary' Rostova"),
                    "file": filename,
                    "line": idx,
                    "matched_text": line.strip()[:60],
                    "message": "Generic default browser font detected without cohesive typography hierarchy. Use Plus Jakarta Sans, Outfit, or modern system stack.",
                    "deduction": 15
                })
                break

    # 3. Enforce responsive viewport meta tag in full HTML documents (.html / .htm)
    if norm_fn.endswith((".html", ".htm")) or (not filename and "<html" in code):
        if "<html" in code and "<head" in code:
            if not re.search(r"""<meta\s+name=["']viewport["']""", code, re.IGNORECASE):
                findings.append({
                    "rule_id": "DESIGN_MISSING_VIEWPORT",
                    "category": "DESIGN",
                    "auditor": COUNCIL_AUDITORS.get("DESIGN", "Elena 'The Visionary' Rostova"),
                    "file": filename,
                    "line": 1,
                    "matched_text": "<head>",
                    "message": "Missing responsive viewport meta tag. Mobile ergonomics violated.",
                    "deduction": 15
                })

    # 4. Ban cliché AI purple/violet palettes (siyohrang taqiqlansin)
    purple_cliche_pattern = r"""(?i)(?:\b(?:from|to|via|bg|text|border)-purple-[4-9]00\b|#(?:9333ea|a855f7|7e22ce|c084fc|7c3aed|8b5cf6)\b)"""
    for idx, line in enumerate(lines, 1):
        if re.search(purple_cliche_pattern, line):
            if not is_ignored(line):
                findings.append({
                    "rule_id": "DESIGN_BANNED_PURPLE_CLICHE",
                    "category": "DESIGN",
                    "auditor": COUNCIL_AUDITORS.get("DESIGN", "Elena 'The Visionary' Rostova"),
                    "file": filename,
                    "line": idx,
                    "matched_text": line.strip()[:60],
                    "message": "Stereotypical AI purple/violet palette cliché detected. Elena Rostova Invariant: Use mature, industry-grade palettes (electric cyan #06b6d4, sapphire #2563eb, emerald #10b981, champagne #f59e0b, or monochrome obsidian titanium).",
                    "deduction": 20
                })
                break

    return findings


def scan_code(code: str, filename: str = "", config: Optional[Dict[str, Any]] = None, config_override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Audits a string of source code against all Artisan rules.
    Respects inline 'artisan-ignore' markers and artisan.config.json toggles.
    Returns deterministic status, score, flaws, and detailed findings.
    """
    if config is None:
        config = config_override if config_override is not None else load_artisan_config(".")

    rules_cfg = config.get("rules", {})
    findings: List[Dict[str, Any]] = []
    lines = code.splitlines()

    for line_idx, line in enumerate(lines, 1):
        if is_ignored(line):
            continue

        for rule_id, category, compiled_pattern, message, deduction in COMPILED_RULES:
            if not is_rule_enabled(rule_id, rules_cfg):
                continue

            match = compiled_pattern.search(line)
            if match:
                # Intelligent false-positive suppression for SECRET_ASSIGNMENT
                if rule_id == "SECRET_ASSIGNMENT":
                    assigned_val = match.group(1).strip() if match.groups() else ""
                    norm_val = assigned_val.lower().strip("\"' ")
                    is_test_env = any(t in filename.lower().replace("\\", "/") for t in ["test", "bench", "fixture", "mock", "sample"])
                    if norm_val in DUMMY_SECRET_VALUES or norm_val.startswith(("test", "dummy", "fake", "placeholder", "mock", "sample", "temp_")):
                        continue
                    if is_test_env and (len(norm_val) <= 12 or norm_val.isalnum()):
                        # Suppress short dummy test strings inside test suites unless matching specific token prefixes
                        continue

                findings.append({
                    "rule_id": rule_id,
                    "category": category,
                    "auditor": COUNCIL_AUDITORS.get(category, "Hallwright Council"),
                    "file": filename,
                    "line": line_idx,
                    "matched_text": line.strip()[:80],
                    "message": message,
                    "deduction": deduction
                })

    # Custom organizational rules evaluation (.hallwright/rules.json or config)
    custom_rules = config.get("custom_rules", [])
    if custom_rules:
        for crule in custom_rules:
            c_id = crule.get("id", "CUSTOM_RULE")
            c_pattern = crule.get("pattern", "")
            if not c_pattern or not is_rule_enabled(c_id, rules_cfg):
                continue
            c_category = crule.get("category", "CUSTOM")
            c_message = crule.get("message", f"Custom rule violation: {c_id}")
            c_deduction = int(crule.get("deduction", 20))
            c_exts = crule.get("extensions", [])

            if c_exts and filename:
                norm_f = filename.lower().replace("\\", "/")
                if not any(norm_f.endswith(ext.lower()) for ext in c_exts):
                    continue

            try:
                c_compiled = re.compile(c_pattern, re.IGNORECASE if crule.get("ignore_case", True) else 0)
            except re.error:
                continue

            for line_idx, line in enumerate(lines, 1):
                if is_ignored(line):
                    continue
                if c_compiled.search(line):
                    findings.append({
                        "rule_id": c_id,
                        "category": c_category,
                        "auditor": COUNCIL_AUDITORS.get(c_category, "Hallwright Custom Auditor"),
                        "file": filename,
                        "line": line_idx,
                        "matched_text": line.strip()[:80],
                        "message": c_message,
                        "deduction": c_deduction
                    })

    # Multi-line block comments scanner (/* ... */, """ ... """, <!-- ... -->)
    block_comment_pattern = re.compile(
        r"(?:/\*[\s\S]*?\*/|<!--[\s\S]*?-->|(?:\"\"\"|''')[\s\S]*?(?:\"\"\"|'''))",
        re.IGNORECASE
    )
    for match in block_comment_pattern.finditer(code):
        block_text = match.group(0)
        if is_ignored(block_text):
            continue
        if re.search(r"\b(?:todo|fixme|xxx|hack|tbd|stub)\b|\bimplement\s+later\b", block_text, re.IGNORECASE):
            start_pos = match.start()
            line_no = code[:start_pos].count("\n") + 1
            if not any(f["rule_id"] == "STUB_TODO_FIXME" and f["line"] == line_no for f in findings):
                findings.append({
                    "rule_id": "STUB_TODO_FIXME",
                    "category": "STUB",
                    "auditor": COUNCIL_AUDITORS["STUB"],
                    "file": filename,
                    "line": line_no,
                    "matched_text": block_text.strip().splitlines()[0][:80],
                    "message": "Unfinished multi-line block stub or placeholder detected. Complete all logic end-to-end.",
                    "deduction": 20
                })

    # Check for empty catch or except spanning across multiple lines if not caught per line
    if not any(f["rule_id"] == "STUB_EMPTY_CATCH" for f in findings):
        for m in re.finditer(r"catch\s*(?:\([^)]*\))?\s*\{\s*\}", code):
            start_pos = m.start()
            line_no = code[:start_pos].count("\n") + 1
            line_str = lines[line_no - 1] if line_no <= len(lines) else ""
            if not is_ignored(line_str):
                findings.append({
                    "rule_id": "STUB_EMPTY_CATCH",
                    "category": "STUB",
                    "auditor": COUNCIL_AUDITORS["STUB"],
                    "file": filename,
                    "line": line_no,
                    "matched_text": m.group(0),
                    "message": "Empty catch block detected. Handle or log exceptions properly.",
                    "deduction": 25
                })
                break

    if not any(f["rule_id"] == "STUB_BARE_EXCEPT" for f in findings):
        for m in re.finditer(r"except(?:\s+Exception(?:\s+as\s+[a-zA-Z0-9_]+)?)?\s*:\s*\n\s*pass\b", code):
            start_pos = m.start()
            line_no = code[:start_pos].count("\n") + 1
            except_line = lines[line_no - 1] if line_no <= len(lines) else ""
            pass_line = lines[line_no] if line_no < len(lines) else ""
            if not is_ignored(except_line) and not is_ignored(pass_line):
                findings.append({
                    "rule_id": "STUB_BARE_EXCEPT",
                    "category": "STUB",
                    "auditor": COUNCIL_AUDITORS["STUB"],
                    "file": filename,
                    "line": line_no,
                    "matched_text": m.group(0),
                    "message": "Silent exception suppression. Log or handle errors.",  # hallwright-ignore
                    "deduction": 25
                })
                break

    # Deep AST analysis for Python code (eliminates regex blindspots)
    if filename.endswith(".py") or ("def " in code and ("import " in code or "try:" in code)):
        ast_results = scan_python_ast(code, filename=filename)
        existing_keys = {(f["rule_id"], f["line"]) for f in findings}
        for item in ast_results:
            if (item["rule_id"], item["line"]) not in existing_keys:
                findings.append(item)

    # Multi-language structural analysis (JS/TS/Go/Java)
    struct_results = scan_multilingual_structural(code, filename=filename)
    existing_keys = {(f["rule_id"], f["line"]) for f in findings}
    for item in struct_results:
        if (item["rule_id"], item["line"]) not in existing_keys:
            findings.append(item)

    # Elena Rostova UI/UX Craftsmanship & Anti-Generic Guardrail
    design_results = scan_ui_design_standards(code, filename=filename)
    existing_keys = {(f["rule_id"], f["line"]) for f in findings}
    for item in design_results:
        if (item["rule_id"], item["line"]) not in existing_keys:
            findings.append(item)

    total_deduction = sum(f["deduction"] for f in findings)
    score = max(0, 100 - total_deduction)

    flaw_messages = [f"[{f['category']}] line {f['line']}: {f['message']}" for f in findings]

    if findings:
        status = "REJECTED"
        verdict = f"Rejected: {len(findings)} defect(s) detected. Autonomously remediate all flaws."
        auditor = "Gabriel 'The Sentinel' Frost (Cybersecurity & Quality Auditor)"
    else:
        status = "CERTIFIED"
        score = 100
        verdict = "Certified: All quality and security checks passed."
        auditor = "Marcus 'The Vanguard' Sterling (Engineering Lead)"

    return {
        "status": status,
        "score": score,
        "flaws": flaw_messages,
        "findings": findings,
        "auditor": auditor,
        "verdict": verdict
    }


def scan_file(filepath: str, config: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Scans an individual file on disk."""
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return scan_code(content, filename=filepath, config=config)
    except (OSError, UnicodeDecodeError):
        return None


def get_staged_git_files() -> List[str]:
    """Returns a list of currently staged files in git."""
    try:
        proc = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if proc.returncode == 0:
            return [f.strip() for f in proc.stdout.splitlines() if f.strip()]
    except (subprocess.SubprocessError, OSError):
        return []


DEFAULT_BASELINE_PATH = os.path.join(".hallwright", "baseline.json")


def load_baseline(base_dir: str = ".", custom_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Loads existing technical debt baseline from .hallwright/baseline.json or custom path."""
    candidates = []
    if custom_path:
        candidates.append(custom_path)
    candidates.append(os.path.join(base_dir, ".hallwright", "baseline.json"))
    candidates.append(os.path.join(base_dir, "baseline.json"))

    for p in candidates:
        if os.path.isfile(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "flaws" in data:
                        return data
                    elif isinstance(data, list):
                        return {"flaws": data}
            except (OSError, json.JSONDecodeError):
                continue
    return None


def is_flaw_in_baseline(flaw: Dict[str, Any], baseline_flaws: List[Dict[str, Any]]) -> bool:
    """Matches a newly detected flaw against recorded baseline debt items."""
    flaw_file = flaw.get("file", "").replace("\\", "/").lstrip("./")
    flaw_rule = flaw.get("rule_id", "")
    flaw_text = flaw.get("matched_text", "").strip()
    flaw_line = int(flaw.get("line", 0))

    for b in baseline_flaws:
        b_file = b.get("file", "").replace("\\", "/").lstrip("./")
        b_rule = b.get("rule_id", "")
        if b_file == flaw_file and b_rule == flaw_rule:
            b_text = b.get("matched_text", "").strip()
            if b_text and flaw_text and (b_text == flaw_text or b_text in flaw_text or flaw_text in b_text):
                return True
            if abs(int(b.get("line", 0)) - flaw_line) <= 3:
                return True
    return False


def generate_baseline(base_dir: str = ".", output_path: Optional[str] = None, config_override: Optional[Dict[str, Any]] = None) -> str:
    """Audits workspace ignoring any existing baseline and generates a new .hallwright/baseline.json."""
    from datetime import datetime, timezone

    cfg = config_override or load_artisan_config(base_dir)
    res = scan_project(base_dir=base_dir, staged_only=False, config_override=cfg, ignore_baseline=True)
    all_flaws = res.get("findings", [])

    clean_flaws = []
    for f in all_flaws:
        clean_flaws.append({
            "file": f.get("file", "").replace("\\", "/").lstrip("./"),
            "line": f.get("line", 0),
            "rule_id": f.get("rule_id", ""),
            "category": f.get("category", ""),
            "matched_text": f.get("matched_text", "").strip(),
            "message": f.get("message", "")
        })

    baseline_data = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_flaws": len(clean_flaws),
        "flaws": clean_flaws
    }

    target = output_path or os.path.join(base_dir, ".hallwright", "baseline.json")
    os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(baseline_data, f, indent=2)
        f.write("\n")
    return target


def scan_project(
    base_dir: str = ".",
    staged_only: bool = False,
    config_override: Optional[Dict[str, Any]] = None,
    ignore_baseline: bool = False,
    baseline_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Scans project source files for stubs, secrets, and dangerous execution.
    If staged_only is True, only checks files staged for git commit.
    Uses file-weighted average scoring to avoid dropping a multi-file project to 0 on minor findings.
    Respects artisan.config.json for excluded paths and rule thresholds.
    Filters legacy technical debt matching .hallwright/baseline.json so existing debt does not block commits.
    """
    cfg = config_override or load_artisan_config(base_dir)
    all_findings: List[Dict[str, Any]] = []
    file_scores: List[int] = []
    scanned_count = 0

    # Configurable exclusion list; does not forcibly exclude tests if user wishes to audit test suites (HW-025)
    default_excluded_dirs = {".git", "node_modules", ".venv", "__pycache__"}
    if "exclude_dirs" in cfg:
        excluded_dirs = set(cfg["exclude_dirs"])
    else:
        excluded_dirs = default_excluded_dirs

    excluded_files = set()
    if "exclude_files" in cfg:
        excluded_files.update(cfg["exclude_files"])

    valid_extensions = (".js", ".ts", ".py", ".go", ".rs", ".java", ".cpp", ".cs")

    if staged_only:
        staged_files = get_staged_git_files()
        for filepath in staged_files:
            normalized_path = filepath.replace("\\", "/")
            path_parts = set(normalized_path.split("/"))
            if path_parts & excluded_dirs:
                continue
            if filepath.endswith(valid_extensions):
                filename = os.path.basename(filepath)
                if filename in excluded_files:
                    continue
                scanned_count += 1
                res = scan_file(filepath, config=cfg)
                if res:
                    file_scores.append(res["score"])
                    if res["findings"]:
                        all_findings.extend(res["findings"])
    else:
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith(".")]
            for file in files:
                if file.endswith(valid_extensions):
                    if file in excluded_files:
                        continue
                    filepath = os.path.join(root, file)
                    scanned_count += 1
                    res = scan_file(filepath, config=cfg)
                    if res:
                        file_scores.append(res["score"])
                        if res["findings"]:
                            all_findings.extend(res["findings"])

    # Optional gitleaks pass
    if not staged_only:
        gitleaks_findings = run_gitleaks(base_dir)
        all_findings.extend(gitleaks_findings)

    # Filter findings through baseline if active
    baseline_matched = []
    active_findings = []
    if not ignore_baseline:
        baseline_data = load_baseline(base_dir, custom_path=baseline_path)
        if baseline_data and "flaws" in baseline_data:
            b_flaws = baseline_data["flaws"]
            for f in all_findings:
                if is_flaw_in_baseline(f, b_flaws):
                    baseline_matched.append(f)
                else:
                    active_findings.append(f)
        else:
            active_findings = all_findings
    else:
        active_findings = all_findings

    # Project score and pass/fail are evaluated against active_findings (new regressions)
    critical_findings = [f for f in active_findings if f.get("category") in ("SECRET", "DANGEROUS")]
    warning_findings = [f for f in active_findings if f.get("category") in ("STUB", "AST")]

    mode = cfg.get("mode", "strict").lower()
    threshold = cfg.get("threshold_score", 100)

    # Calculate fair score: if baseline is present, project score reflects absence of new debt
    if baseline_matched:
        active_deductions = sum(f.get("deduction", 20) for f in active_findings)
        project_score = max(0, 100 - active_deductions)
    elif file_scores:
        project_score = round(sum(file_scores) / len(file_scores))
    else:
        project_score = 100

    # In vibe mode, warnings are advisory and never block (always passed = True)
    if mode == "vibe":
        passed = True
    else:
        if threshold >= 100:
            passed = (len(active_findings) == 0)
        else:
            passed = (project_score >= threshold and len(critical_findings) == 0)

    return {
        "passed": passed,
        "mode": mode,
        "scanned_files": scanned_count,
        "findings": active_findings,
        "baseline_findings": baseline_matched,
        "score": project_score,
        "metrics": {
            "critical_count": len(critical_findings),
            "warning_count": len(warning_findings),
            "total_flaws": len(active_findings),
            "baseline_count": len(baseline_matched),
            "average_file_score": project_score
        }
    }


def to_sarif_v2(scan_result: Dict[str, Any]) -> Dict[str, Any]:
    """Converts Hallwright scan results into standard OASIS SARIF v2.1.0 format.

    Compatible with GitHub Code Scanning, GitLab SAST, and IDE SARIF viewers.
    """
    rules_dict = {}
    sarif_results = []

    for f in scan_result.get("findings", []):
        rule_id = f.get("rule_id", "HW_RULE")
        category = f.get("category", "QUALITY")
        message = f.get("message", "Defect detected")
        deduction = f.get("deduction", 10)
        file_path = f.get("file", "unknown").replace("\\", "/")
        line = max(1, f.get("line", 1))

        if deduction >= 25 or category in ("DANGEROUS", "SECURITY", "SECRET"):
            level = "error"
        else:
            level = "warning"

        if rule_id not in rules_dict:
            rules_dict[rule_id] = {
                "id": rule_id,
                "name": rule_id,
                "shortDescription": {"text": message},
                "fullDescription": {"text": f"Hallwright {category} rule: {message}"},
                "defaultConfiguration": {
                    "level": level
                },
                "properties": {
                    "category": category,
                    "deduction": deduction,
                    "auditor": f.get("auditor", "Hallwright Council")
                }
            }

        sarif_results.append({
            "ruleId": rule_id,
            "level": level,
            "message": {
                "text": message
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": file_path
                        },
                        "region": {
                            "startLine": line,
                            "startColumn": 1
                        }
                    }
                }
            ]
        })

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Hallwright",
                        "semanticVersion": "2.0.0",
                        "informationUri": "https://github.com/kapitan00000978-sketch/hallwright",
                        "rules": list(rules_dict.values())
                    }
                },
                "results": sarif_results
            }
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Hallwright Quality & Security Detection Engine")
    parser.add_argument("--file", "-f", help="Scan a specific file")
    parser.add_argument("--staged", "-s", action="store_true", help="Scan only git staged files")
    parser.add_argument("--all", "-a", action="store_true", help="Scan entire project (default)")
    parser.add_argument("--vibe", "-v", action="store_true", help="Run in non-blocking Vibe mode (advisory only)")
    parser.add_argument("--json", "-j", action="store_true", help="Output results in JSON format")
    parser.add_argument("--sarif", action="store_true", help="Output results in OASIS SARIF v2.1.0 format")
    parser.add_argument("--format", choices=["text", "json", "sarif"], default="text", help="Output format")
    parser.add_argument("--baseline", help="Path to custom baseline.json file")
    parser.add_argument("--generate-baseline", action="store_true", help="Generate .hallwright/baseline.json from current workspace debt")

    args = parser.parse_args()
    output_format = "sarif" if args.sarif else ("json" if args.json else args.format)

    cfg = load_artisan_config(".")
    if args.vibe:
        cfg["mode"] = "vibe"

    if args.generate_baseline:
        out_path = generate_baseline(".", output_path=args.baseline, config_override=cfg)
        print(f"✅ [HALLWRIGHT BASELINE]: Generated technical debt baseline at: {out_path}")
        sys.exit(0)

    if args.file:
        res = scan_file(args.file)
        if not res:
            print(f"Error: File not found or unreadable: {args.file}", file=sys.stderr)
            sys.exit(1)
        if output_format == "sarif":
            print(json.dumps(to_sarif_v2({"findings": res.get("flaws_detail", [])}), indent=2))
        elif output_format == "json":
            print(json.dumps(res, indent=2))
        else:
            print(f"[{res['status']}] Score: {res['score']}/100 | File: {args.file}")
            for flaw in res["flaws"]:
                print(f"  • {flaw}")
        sys.exit(0 if res["status"] == "CERTIFIED" else 1)

    result = scan_project(".", staged_only=args.staged, config_override=cfg, baseline_path=args.baseline)

    if output_format == "sarif":
        print(json.dumps(to_sarif_v2(result), indent=2))
    elif output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        scope = "staged files" if args.staged else "all files"
        if result["mode"] == "vibe":
            print(f"⚡ [HALLWRIGHT VIBE MODE ACTIVE]: Rapid development mode. Advisory scan over {result['scanned_files']} {scope}.")
            if result["findings"]:
                print(f"⚡ Advisory notices ({len(result['findings'])} items, Score: {result['score']}/100 - Non-blocking):")
                for f in result["findings"][:10]:
                    auditor = f.get("auditor", "Hallwright Council")
                    print(f"  • {f['file']}:{f['line']} [{f['category']}] [{auditor}] -> {f['message']}")
            else:
                print(f"✅ [HALLWRIGHT VERIFIED]: Clean code. Gate Score: 100/100")
        elif result["passed"]:
            print(f"✅ [HALLWRIGHT VERIFIED]: Scanned {result['scanned_files']} {scope}. Gate Score: {result['score']}/100")
        else:
            print(f"❌ [HALLWRIGHT REJECTED]: Defects detected across {scope}. Gate Score: {result['score']}/100")
            for f in result["findings"][:10]:
                auditor = f.get("auditor", "Hallwright Council")
                print(f"  • {f['file']}:{f['line']} [{f['category']}] [{auditor}] -> {f['message']}")

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
