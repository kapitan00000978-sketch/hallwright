"""
Unit tests for Hallwright Elena Rostova UI/UX Craftsmanship & Anti-Generic Guardrail.
Verifies that the detector rejects flat pitch-black voids, generic fonts, and missing viewports,
protecting AI agents from generating low-effort, dead UI designs.
"""

import os
import sys
import pytest

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
sys.path.insert(0, SCRIPTS_DIR)
from detector import scan_code


def test_ui_guardrail_rejects_flat_pitch_black_void():
    dead_html = """<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dead Black Page</title>
</head>
<body class="bg-black text-white">
  <h1>Generic AI Landing Page</h1>
  <p>Flat black background with zero atmospheric lighting.</p>
</body>
</html>"""
    res = scan_code(dead_html, filename="test_page.html")
    assert res["status"] == "REJECTED"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "DESIGN_FLAT_PITCH_BLACK_VOID" in rule_ids
    assert any("Elena 'The Visionary' Rostova" in f["auditor"] for f in res["findings"])


def test_ui_guardrail_approves_atmospheric_mesh():
    luxury_html = """<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Luxury Page</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body {
      background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #030712 100%);
      color: #f8fafc;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }
  </style>
</head>
<body>
  <div class="ambient-glow-top"></div>
  <canvas id="stars-canvas"></canvas>
  <h1 class="gradient-headline">Elevated Masterpiece</h1>
</body>
</html>"""
    res = scan_code(luxury_html, filename="luxury_page.html")
    assert res["status"] == "CERTIFIED"
    assert res["score"] == 100
    assert len(res["findings"]) == 0


def test_ui_guardrail_rejects_generic_arial_font():
    arial_html = """<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body { font-family: Arial; background: radial-gradient(#fff, #000); }
  </style>
</head>
<body>
  <h1>Page with Arial</h1>
</body>
</html>"""
    res = scan_code(arial_html, filename="arial_page.html")
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "DESIGN_GENERIC_FONT" in rule_ids


def test_ui_guardrail_rejects_missing_viewport():
    no_viewport_html = """<!DOCTYPE html>
<html>
<head>
  <title>No Viewport</title>
  <style>body { background: radial-gradient(#fff, #000); }</style>
</head>
<body>
  <h1>Page without viewport</h1>
</body>
</html>"""
    res = scan_code(no_viewport_html, filename="no_viewport.html")
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "DESIGN_MISSING_VIEWPORT" in rule_ids
