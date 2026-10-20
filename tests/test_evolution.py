"""
Tests for Hallwright Self-Evolution Engine (src/sdk/evolution.py).
Verifies non-blocking background ingestion, vaccine synthesis, generation advancement,
and prompt vaccination.
"""

import os
import sys
import json
import tempfile
import time

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from evolution import SelfEvolutionEngine, ImmunityVaccine


def test_evolution_engine_initialization():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = SelfEvolutionEngine(workspace_root=tmpdir)
        state = engine.load_immune_state()
        assert state["generation"] == 1
        assert state["immunity_score"] >= 90
        assert len(state["vaccines"]) >= 3
        assert state["total_vaccines"] >= 3


def test_evolution_engine_evolve_sync():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = SelfEvolutionEngine(workspace_root=tmpdir)
        initial_gen = engine.load_immune_state()["generation"]

        # Ingest a new defect pattern
        defect = "KeyError: 'auth_token' accessed directly in request handler without validation"
        result = engine.evolve_sync(defect_text=defect, file_path="api/auth.py")

        assert result["status"] == "EVOLVED"
        assert result["generation"] == initial_gen + 1
        assert "secret" in result["vaccine"]["error_signature"].lower() or "credential" in result["vaccine"]["error_signature"].lower()

        # Check ledger persistence
        new_state = engine.load_immune_state()
        assert new_state["generation"] == initial_gen + 1
        assert any(v["id"] == result["vaccine"]["id"] for v in new_state["vaccines"])


def test_evolution_engine_non_blocking_async():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = SelfEvolutionEngine(workspace_root=tmpdir)
        callback_called = []

        def on_evolve(res):
            callback_called.append(res)

        defect = "IndexError: list index 5 out of range in chunk parser"
        # Non-blocking async call
        worker = engine.ingest_and_evolve_async(defect_text=defect, file_path="parser.py", callback=on_evolve)

        # Worker is a running background thread; caller is NOT blocked!
        assert worker.is_alive() or len(callback_called) > 0
        worker.join(timeout=5.0)

        assert len(callback_called) == 1
        assert callback_called[0]["status"] == "EVOLVED"


def test_evolution_engine_duplicate_neutralization():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = SelfEvolutionEngine(workspace_root=tmpdir)
        # Ingest once
        res1 = engine.evolve_sync("ZeroDivisionError: integer division by zero in metric calculation")
        assert res1["status"] in ("EVOLVED", "ALREADY_IMMUNIZED")

        # Ingest exact same defect again
        res2 = engine.evolve_sync("ZeroDivisionError: integer division by zero in metric calculation")
        assert res2["status"] == "ALREADY_IMMUNIZED"


def test_evolution_engine_vaccination_prompt_injection():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = SelfEvolutionEngine(workspace_root=tmpdir)
        prompt_injection = engine.get_vaccination_prompt_injection("Design secure auth API")
        assert "Autonomous Project Immunity" in prompt_injection
        assert "Generation" in prompt_injection
        assert "invariants" in prompt_injection.lower() or "strictly" in prompt_injection.lower()

