"""
Tests for Hallwright Sentinel TUI Dashboard (cli/dashboard.py).
Verifies real-time telemetry, 11-Titan swarm status, prompt elevation integration,
and non-interactive CLI flags.
"""

import sys
import os
import json
import subprocess
from io import StringIO
from unittest.mock import patch

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "cli"))
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

import dashboard


def test_dashboard_get_telemetry():
    telemetry = dashboard.get_telemetry()
    assert isinstance(telemetry, dict)
    assert telemetry["protocol_status"] == "ACTIVE"
    assert telemetry["gatekeeper_score"] == 100
    assert telemetry["active_subagents"] == 11
    assert "timestamp" in telemetry
    assert "web_healed_count" in telemetry


def test_dashboard_render_sentinel_hud_output():
    telemetry = dashboard.get_telemetry()
    captured = StringIO()
    with patch("sys.stdout", captured):
        dashboard.render_sentinel_hud(telemetry, once=True)
    out = captured.getvalue()
    assert "HALLWRIGHT SENTINEL TUI" in out
    assert "11 TITANS" in out
    # Verify all 11 subagents are displayed in roster
    for expected_agent in [
        "architect", "database", "ai", "security", "designer",
        "performance", "devops", "tester", "critic", "healer", "copywriter"
    ]:
        assert expected_agent in out


def test_dashboard_action_prompt_passthrough_and_elevation():
    # 1. Underspecified prompt -> Elevation
    captured_elevated = StringIO()
    with patch("sys.stdout", captured_elevated):
        dashboard.action_prompt("fix bug")
    elevated_out = captured_elevated.getvalue()
    assert "ELEVATION_APPLIED" in elevated_out
    assert "Quality Radar Score:" in elevated_out

    # 2. Comprehensive prompt -> Passthrough
    detailed_prompt = (
        "Implement a Python function to parse JSON with schema validation using pydantic, "
        "handling ValidationError with logging, ensuring 100% test coverage using pytest."
    )
    captured_pass = StringIO()
    with patch("sys.stdout", captured_pass):
        dashboard.action_prompt(detailed_prompt)
    pass_out = captured_pass.getvalue()
    assert "PASSTHROUGH_OPTIMAL" in pass_out
    assert detailed_prompt in pass_out


def test_dashboard_show_council_details_search():
    captured = StringIO()
    with patch("sys.stdout", captured):
        dashboard.show_council_details("Gabriel")
    out = captured.getvalue()
    assert "Gabriel 'The Sentinel' Frost" in out
    assert "Cybersecurity" in out


def test_dashboard_cli_subprocess_once_and_json():
    dashboard_path = os.path.join(ROOT_DIR, "cli", "dashboard.py")

    # --once flag
    res_once = subprocess.run([sys.executable, dashboard_path, "--once"], capture_output=True, text=True)
    assert res_once.returncode == 0
    assert "HALLWRIGHT SENTINEL TUI" in res_once.stdout
    assert "11 TITANS" in res_once.stdout

    # --json flag
    res_json = subprocess.run([sys.executable, dashboard_path, "--json"], capture_output=True, text=True)
    assert res_json.returncode == 0
    data = json.loads(res_json.stdout)
    assert data["protocol_status"] == "ACTIVE"
    assert data["active_subagents"] == 11
