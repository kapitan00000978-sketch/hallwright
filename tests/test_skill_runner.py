"""Tests for Hallwright Active Skill Execution Engine (src/sdk/skill_runner.py).
Verifies skill discovery, parsing, execution, tier transitions, and evaluations.
"""

import os
import sys
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from skill_runner import SkillEngine, SkillMetadata


def test_discover_skills():
    engine = SkillEngine(workspace_root=ROOT_DIR)
    skills = engine.discover_skills()
    assert len(skills) >= 10
    assert "craftsman-evaluator" in skills
    assert "adversarial-code-review" in skills
    assert "tier-3-sovereign" in skills


def test_execute_tier_skill():
    engine = SkillEngine(workspace_root=ROOT_DIR)
    res = engine.execute_skill("tier-3-sovereign")
    assert res["status"] == "ACTIVATED"
    assert res["tier"] == 3
    assert res["full_access"] is True


def test_execute_craftsman_evaluator():
    engine = SkillEngine(workspace_root=ROOT_DIR)
    target = os.path.join(ROOT_DIR, "hallwright_cli.py")
    res = engine.execute_skill("craftsman-evaluator", target=target)
    assert res["status"] in ("APPROVED", "NEEDS_IMPROVEMENT")
    assert "score" in res
    assert res["score"] >= 75


def test_execute_adversarial_review():
    engine = SkillEngine(workspace_root=ROOT_DIR)
    target = os.path.join(ROOT_DIR, "hallwright_cli.py")
    res = engine.execute_skill("adversarial-code-review", target=target)
    assert res["skill"] == "adversarial-code-review"
    assert "pass_score" in res


def test_execute_systematic_debugging():
    engine = SkillEngine(workspace_root=ROOT_DIR)
    res = engine.execute_skill("systematic-debugging", context={"error": "Connection reset by peer"})
    assert res["status"] == "DIAGNOSED"
    assert len(res["steps"]) == 4


def test_execute_unknown_skill_returns_error():
    engine = SkillEngine(workspace_root=ROOT_DIR)
    res = engine.execute_skill("nonexistent-magic-skill-xyz")
    assert res["status"] == "NOT_FOUND"
