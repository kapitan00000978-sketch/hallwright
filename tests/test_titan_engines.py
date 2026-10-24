"""
Unit Tests for Hallwright Titan-Tier Engines:
1. VisualVerifier (src/sdk/visual_verifier.py)
2. CombatArena (src/sdk/combat_arena.py)
3. ImmuneEngine (src/sdk/immune_engine.py)
4. WebHudServer (src/sdk/web_hud.py)
5. ProjectDoctor (src/sdk/project_doctor.py)
"""

import os
import sys
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from visual_verifier import VisualVerifier
from combat_arena import CombatArena
from immune_engine import ImmuneEngine
from web_hud import WebHudServer
from project_doctor import ProjectDoctor


def test_visual_verifier_clean_html():
    verifier = VisualVerifier(workspace_root=ROOT_DIR)
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Verified UI</title>
      <style>body { margin:0; font-family:sans-serif; overflow-x:hidden; }</style>
    </head>
    <body>
      <main style="padding:2rem;"><h1>Hello World</h1></main>
    </body>
    </html>"""
    report = verifier.inspect_html_content(html, "clean.html")
    assert report.passed is True
    assert report.score >= 80
    assert report.meta_tags_verified is True
    assert len(report.console_errors) == 0


def test_visual_verifier_detects_defects():
    verifier = VisualVerifier(workspace_root=ROOT_DIR)
    bad_html = """<html><body><script>const x = '${{bad_interpolation}}';</script></body></html>"""
    report = verifier.inspect_html_content(bad_html, "bad.html")
    assert report.passed is False
    assert len(report.console_errors) >= 1


def test_combat_arena_evaluates_code_defense():
    arena = CombatArena(workspace_root=ROOT_DIR)
    safe_code = """
    import sqlite3
    def get_user(conn, user_id: int):
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()
    """
    ledger = arena.evaluate_code_defense(safe_code, "safe_service.py")
    assert ledger.total_rounds >= 6
    assert ledger.survival_coefficient >= 80.0
    assert ledger.verdict in ("APPROVED", "CONDITIONAL")


def test_combat_arena_detects_raw_sql_breach():
    arena = CombatArena(workspace_root=ROOT_DIR)
    unsafe_code = """
    def get_user(conn, user_id):
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    """
    ledger = arena.evaluate_code_defense(unsafe_code, "unsafe_service.py")
    sql_rounds = [r for r in ledger.rounds if r.attack.category == "SQL_INJECTION"]
    assert any(not r.defended for r in sql_rounds)


def test_immune_engine_antibodies_and_scan():
    engine = ImmuneEngine(workspace_root=ROOT_DIR)
    assert len(engine.antibodies) >= 4
    
    # Synthesize an antibody
    ab = engine.synthesize_antibody(
        name="Test Anti-Leak Antibody",
        category="SECURITY",
        pattern=r'LEAK_TOKEN_KEY_[0-9]+',
        remedy_template="Use os.getenv('TOKEN_KEY')",
        description="Prevents leak token variables.",
    )
    assert ab.id.startswith("ANTIBODY-")
    assert os.path.exists(ab.vaccine_test_path)


def test_web_hud_telemetry_and_html():
    hud = WebHudServer(port=7331, workspace_root=ROOT_DIR)
    telem = hud.get_system_telemetry()
    assert telem["gatekeeper_score"] == 100
    assert telem["lyapunov_exponent"] > 0.0
    assert len(telem["agents_connected"]) >= 3
    
    html = hud.render_hud_html()
    assert "HALLWRIGHT TITAN HUD" in html
    assert "chaosCanvas" in html


def test_project_doctor_diagnosis_and_healing(tmp_path):
    doctor = ProjectDoctor(workspace_root=str(tmp_path))
    diag = doctor.diagnose()
    assert diag.overall_health_score < 100
    
    # Heal the project
    healed_diag = doctor.heal()
    assert len(healed_diag.healed_items) >= 1
    assert (tmp_path / "AGENTS.md").exists()
