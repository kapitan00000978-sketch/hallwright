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


def test_ui_guardrail_rejects_purple_cliche():
    purple_html = """<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Purple Cliche Page</title>
  <style>body { background: radial-gradient(#fff, #000); }</style>
</head>
<body>
  <div class="from-purple-600 to-indigo-600">
    <button class="bg-purple-500">Boring AI Purple</button>
  </div>
</body>
</html>"""
    res = scan_code(purple_html, filename="purple_page.html")
    assert res["status"] == "REJECTED"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "DESIGN_BANNED_PURPLE_CLICHE" in rule_ids
    flaw = next(f for f in res["findings"] if f["rule_id"] == "DESIGN_BANNED_PURPLE_CLICHE")
    assert "electric cyan" in flaw["message"]


def test_ui_guardrail_rejects_janky_layout_reflow_animation():
    janky_html = """<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Janky Animation</title>
  <style>
    body { background: radial-gradient(#06b6d4, #000); }
    .sidebar { transition: width 0.3s; }
  </style>
</head>
<body><h1>Janky reflow</h1></body>
</html>"""
    res = scan_code(janky_html, filename="janky_anim.html")
    assert res["status"] == "REJECTED"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "DESIGN_JANKY_ANIMATION_REFLOW" in rule_ids


def test_ui_guardrail_rejects_robotic_linear_transition():
    linear_html = """<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Linear Transition</title>
  <style>
    body { background: radial-gradient(#06b6d4, #000); }
    .btn { transition: all 0.2s linear; }
  </style>
</head>
<body><button class="btn">Robotic Button</button></body>
</html>"""
    res = scan_code(linear_html, filename="linear_anim.html")
    assert res["status"] == "REJECTED"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "DESIGN_ROBOTIC_LINEAR_ANIMATION" in rule_ids


def test_ui_guardrail_rejects_hyperactive_spin():
    hyper_html = """<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hyperactive Page</title>
  <style>
    body { background: radial-gradient(#06b6d4, #000); }
    .bad-badge { animation: spin 1s infinite; }
  </style>
</head>
<body><div class="bad-badge">Spinning</div></body>
</html>"""
    res = scan_code(hyper_html, filename="hyper_anim.html")
    assert res["status"] == "REJECTED"
    rule_ids = [f["rule_id"] for f in res["findings"]]
    assert "DESIGN_HYPERACTIVE_ANIMATION" in rule_ids


def test_ui_guardrail_approves_fluid_gpu_physics():
    fluid_html = """<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>60FPS Fluid Page</title>
  <style>
    body {
      background: radial-gradient(#06b6d4, #000);
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .card {
      will-change: transform, opacity;
      transform: translateZ(0);
      transition: transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.28s ease;
    }
    .card:hover {
      transform: translateY(-4px) scale(1.01);
    }
  </style>
</head>
<body>
  <div class="card">Butter smooth 60FPS physics</div>
</body>
</html>"""
    res = scan_code(fluid_html, filename="fluid_anim.html")
    assert res["status"] == "CERTIFIED"
    assert res["score"] == 100
    assert len(res["findings"]) == 0


