"""
Unit tests for Hallwright v0.10.87 Autonomous Visual Transmuter (visual_transmuter.py).
Verifies:
- Automated visual saliency auditing (headings, modular cards, buttons, viewport meta).
- HTML transmutation: upgrading flat cards to magic-border-beam, injecting 3D canvas and kbar.
- File-based transmutation.
- MCP tool dispatch for hallwright_transmute_ui.
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "sdk")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp")))

from visual_transmuter import VisualTransmuter
import server as mcp_server


DULL_HTML_SAMPLE = """<!DOCTYPE html>
<html>
<head>
  <title>Oddiy Katalog</title>
</head>
<body>
  <h1>Tibbiy Uskunalar Markazi</h1>
  <div class="product-card">
    <h3>UZI Uskunasi</h3>
    <p>Narxi: 12,000$</p>
    <button>Sotib olish</button>
  </div>
  <div class="category-box">
    <h3>Tibbiy Buyumlar</h3>
    <p>Shpritslar va dokalar</p>
  </div>
</body>
</html>"""


def test_audit_visual_saliency():
    transmuter = VisualTransmuter()
    audit = transmuter.audit_visual_saliency(DULL_HTML_SAMPLE)

    assert audit["h1_count"] == 1
    assert audit["card_elements_found"] == 2
    assert audit["cta_buttons_found"] == 1
    assert audit["score"] >= 60
    assert audit["grade"] in ("AAA", "AA", "A")


def test_transmute_html():
    transmuter = VisualTransmuter()
    result = transmuter.transmute_html(DULL_HTML_SAMPLE)

    assert result["status"] == "TRANSMUTED"
    assert result["upgrades_count"] >= 2
    html = result["html"]

    # Verify injected primitives
    assert "magic-border-beam" in html
    assert "spatial-hero-canvas" in html
    assert "kbar-overlay" in html
    assert "Plus Jakarta Sans" in html
    assert "KbarCommandHub" in html
    # Invariant: Gabriel Frost security - zero raw innerHTML
    assert "innerHTML" not in html


def test_transmute_file(tmp_path):
    transmuter = VisualTransmuter()
    input_file = tmp_path / "old_page.html"
    input_file.write_text(DULL_HTML_SAMPLE, encoding="utf-8")

    out_file = tmp_path / "upgraded_page.html"
    res = transmuter.transmute_file(str(input_file), str(out_file))

    assert res["status"] == "TRANSMUTED"
    assert os.path.exists(str(out_file))
    content = out_file.read_text(encoding="utf-8")
    assert "magic-border-beam" in content


def test_mcp_transmute_ui_dispatch():
    req = {
        "jsonrpc": "2.0",
        "id": "transmute-test-1",
        "method": "tools/call",
        "params": {
            "name": "hallwright_transmute_ui",
            "arguments": {
                "html": DULL_HTML_SAMPLE
            }
        }
    }
    resp = mcp_server.dispatch_request(req)
    assert resp["id"] == "transmute-test-1"
    assert "result" in resp
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["status"] == "TRANSMUTED"
    assert content["upgrades_count"] >= 2
