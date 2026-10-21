"""
Unit tests for Hallwright v0.10.87 Visual Primitives Engine.
Verifies integration of Magic UI, React Three Fiber, Drei, Park UI, and kbar.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "sdk")))
from visual_primitives import VisualPrimitivesEngine
import hallwright_cli


def test_visual_primitives_vendor_discovery():
    engine = VisualPrimitivesEngine()
    vendors = engine.available_vendor_modules
    assert len(vendors) >= 5
    assert "magicui" in vendors
    assert "react-three-fiber" in vendors
    assert "drei" in vendors
    assert "park-ui" in vendors
    assert "kbar" in vendors


def test_magic_ui_css_tokens():
    engine = VisualPrimitivesEngine()
    css = engine.get_magic_ui_css()
    assert ".magic-border-beam" in css
    assert ".magic-bento-grid" in css
    assert ".magic-dock" in css
    assert ".kbar-overlay" in css
    assert ".spatial-canvas-container" in css


def test_kbar_markup_and_script():
    engine = VisualPrimitivesEngine()
    html = engine.get_kbar_html()
    assert "id=\"kbar-overlay\"" in html
    assert "id=\"kbar-input\"" in html
    assert "id=\"kbar-list\"" in html

    js = engine.get_visual_engine_js()
    assert "class KbarCommandHub" in js
    assert "class SpatialCanvasEngine" in js
    # Invariant: Gabriel Frost XSS defense - zero raw innerHTML
    assert "innerHTML" not in js


def test_project_version_v0_10_87():
    # Verify version lock across CLI and project
    assert hallwright_cli.__version__ == "0.10.87"
    version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "VERSION")
    assert os.path.exists(version_file)
    with open(version_file, "r", encoding="utf-8") as f:
        v_content = f.read().strip()
    assert v_content == "v0.10.87"
