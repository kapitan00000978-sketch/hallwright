import os
import sys
import tempfile
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from arena import AdversarialArena, AttackVector


def test_arena_initialization():
    arena = AdversarialArena()
    assert arena is not None
    assert len(arena.DEFAULT_VECTORS) >= 4


def test_arena_simulation_execution():
    with tempfile.TemporaryDirectory() as tmpdir:
        arena = AdversarialArena(workspace_root=tmpdir)
        results = arena.execute_simulation()
        assert results["status"] in ("VICTORY", "DEFEATED")
        assert results["defense_score"] >= 90
        assert len(results["rounds"]) >= 4
        for r in results["rounds"]:
            assert "vector_id" in r
            assert "defense_rule_applied" in r


def test_arena_auto_evolution_on_novel_breach():
    with tempfile.TemporaryDirectory() as tmpdir:
        arena = AdversarialArena(workspace_root=tmpdir)
        novel_vector = AttackVector(
            id="atk-custom-001",
            category="runtime",
            name="Novel Memory Buffer Desync",
            payload="malformed_buffer_frame",
            expected_error="TypeError: unexpected type operation without typeguard",
            description="Exposes unvalidated type cast"
        )
        sim_res = arena.execute_simulation(vectors=[novel_vector], auto_evolve=True)
        assert sim_res["defense_score"] == 100
        assert len(sim_res["rounds"]) == 1
        assert sim_res["rounds"][0]["breached"] is False
