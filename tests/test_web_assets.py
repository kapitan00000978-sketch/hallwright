"""
Tests for Web Playground static assets.
Part of Pillar VIII: Browser WebAssembly & Serverless Playground (Bosqich 89-98).
"""

import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(ROOT_DIR, "web")


def test_web_playground_assets_exist():
    html_path = os.path.join(WEB_DIR, "index.html")
    css_path = os.path.join(WEB_DIR, "style.css")
    js_path = os.path.join(WEB_DIR, "playground.js")

    assert os.path.isfile(html_path)
    assert os.path.isfile(css_path)
    assert os.path.isfile(js_path)

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        assert "HALLWRIGHT" in html
        assert "codeEditor" in html
        assert "remediateBtn" in html

    with open(js_path, "r", encoding="utf-8") as f:
        js = f.read()
        assert "auditCode" in js
        assert "autoHealCode" in js
