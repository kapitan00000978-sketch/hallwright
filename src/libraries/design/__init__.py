"""Hallwright Enterprise Design & 3D Spatial Library.

Exposes file paths and static asset helpers for:
- spatial_3d.js: Standalone zero-dependency 3D canvas engine
- liquid_glass.css: Apple-grade glassmorphism CSS design system
- dashboard_3d.html: Interactive 3D HUD & Swarm visualizer
"""

import os
from typing import Dict, Optional

_DESIGN_DIR = os.path.dirname(os.path.abspath(__file__))


def get_asset_path(filename: str) -> str:
    """Return the absolute path to a design asset."""
    path = os.path.join(_DESIGN_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Design asset '{filename}' not found in {_DESIGN_DIR}.")
    return path


def get_dashboard_html() -> str:
    """Return raw HTML content of the 3D dashboard."""
    with open(get_asset_path("dashboard_3d.html"), "r", encoding="utf-8") as f:
        return f.read()


__all__ = [
    "get_asset_path",
    "get_dashboard_html",
]
