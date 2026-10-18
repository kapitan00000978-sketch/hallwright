"""
Tests for Hallwright Adversarial Code Reviewer & Critic Engine (src/sdk/reviewer.py).
Verifies red-team security audits, resilience checks, scar tissue detection, and PR markdown output.
"""

import os
import sys
import tempfile
import json
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from reviewer import AdversarialReviewer


def test_review_clean_code():
    reviewer = AdversarialReviewer()
    clean_code = """
def compute_total(items):
    total = 0
    for item in items:
        total += item['price'] * item['quantity']
    return total
"""
    report = reviewer.review_text(clean_code, file_path="calculator.py")
    assert report["passed"] is True
    assert report["score"] == 100.0
    assert report["verdict"] == "APPROVED_FOR_PRODUCTION"
    assert report["defects_count"] == 0


def test_review_security_vulnerabilities():
    reviewer = AdversarialReviewer()
    flawed_code = """
import os
import subprocess

def run_command(user_input):
    os.system(user_input)
    subprocess.run("ls " + user_input, shell=True)
    eval("2 + 2")
"""
    report = reviewer.review_text(flawed_code, file_path="runner.py")
    assert report["passed"] is False
    assert report["verdict"] == "VETO_REVISION_REQUIRED"
    assert report["score"] < 70.0

    categories = [f["category"] for f in report["findings"]]
    severities = [f["severity"] for f in report["findings"]]
    assert "SECURITY" in categories
    assert "CRITICAL" in severities


def test_review_resilience_and_stubs():
    reviewer = AdversarialReviewer()
    flawed_code = """
def process_data():
    # TODO: implement real database sync later
    try:
        do_something()
    except Exception:
        pass
"""
    report = reviewer.review_text(flawed_code, file_path="worker.py")
    assert report["passed"] is False
    assert report["verdict"] == "VETO_REVISION_REQUIRED"

    messages = [f["message"] for f in report["findings"]]
    assert any("Silent exception suppression" in m for m in messages)
    assert any("stub" in m.lower() for m in messages)


def test_review_scar_tissue_regression():
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_path = os.path.join(tmpdir, "memory.json")
        with open(mem_path, "w", encoding="utf-8") as f:
            json.dump({
                "version": "2.0.0",
                "mistakes": [
                    {
                        "id": "mis-0099",
                        "category": "auth",
                        "pattern": "jwt_none_alg",
                        "lesson": "Always verify JWT signature algorithm is asymmetric or HS256."
                    }
                ],
                "scarTissue": []
            }, f)

        reviewer = AdversarialReviewer(memory_path=mem_path)
        regressive_code = """
def verify_token(token):
    # This uses jwt_none_alg bypass
    return parse_raw(token)
"""
        report = reviewer.review_text(regressive_code, file_path="auth.py")
        assert report["passed"] is False
        scar_tissue_findings = [f for f in report["findings"] if f["category"] == "SCAR_TISSUE"]
        assert len(scar_tissue_findings) >= 1
        assert "mis-0099" in scar_tissue_findings[0]["message"]


def test_review_git_diff_parsing():
    reviewer = AdversarialReviewer()
    sample_diff = """diff --git a/app.py b/app.py
index 1234567..89abcdef 100644
--- a/app.py
+++ b/app.py
@@ -10,3 +10,4 @@ def main():
     print("starting")
+    eval("malicious()")
"""
    report = reviewer.review_diff(diff_text=sample_diff)
    assert report["passed"] is False
    assert report["defects_count"] == 1
    assert report["findings"][0]["file"] == "app.py"
    assert report["findings"][0]["line"] == 11


def test_format_markdown_review():
    reviewer = AdversarialReviewer()
    clean_report = reviewer.review_text("x = 1\n", file_path="test.py")
    md = reviewer.format_markdown_review(clean_report)
    assert "## 🛡️ Hallwright Adversarial Code Review" in md
    assert "APPROVED" in md

    flawed_report = reviewer.review_text("eval('evil')\n", file_path="vuln.py")
    flawed_md = reviewer.format_markdown_review(flawed_report)
    assert "VETO / REVISION REQUIRED" in flawed_md
    assert "Defect Ledger" in flawed_md
    assert "Gabriel Frost" in flawed_md
