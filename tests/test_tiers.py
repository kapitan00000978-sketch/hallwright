import os
import sys
import tempfile
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from tiers import SkillTierEngine, TierLevel, TIER_POLICIES


def test_tier_default_is_tier_3():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = os.path.join(tmpdir, "tier_config.json")
        engine = SkillTierEngine(config_path=cfg)
        policy = engine.get_active_tier()
        assert policy.tier == TierLevel.TIER_3_SOVEREIGN
        assert policy.full_access is True
        assert policy.can_execute_swarm is True
        assert policy.can_evolve_immune_system is True


def test_set_active_tier_and_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = os.path.join(tmpdir, "tier_config.json")
        engine = SkillTierEngine(config_path=cfg)

        # Set to Tier 1
        p1 = engine.set_active_tier(1)
        assert p1.tier == 1
        assert p1.full_access is False
        assert p1.can_modify_files is False

        # Reload from same config
        engine2 = SkillTierEngine(config_path=cfg)
        p1_reloaded = engine2.get_active_tier()
        assert p1_reloaded.tier == 1

        # Set to Tier 2
        p2 = engine.set_active_tier(2)
        assert p2.tier == 2
        assert p2.can_modify_files is True
        assert p2.can_execute_swarm is False

        # Set back to Tier 3
        p3 = engine.set_active_tier(3)
        assert p3.tier == 3
        assert p3.full_access is True


def test_invalid_tier_raises_error():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = os.path.join(tmpdir, "tier_config.json")
        engine = SkillTierEngine(config_path=cfg)
        with pytest.raises(ValueError):
            engine.set_active_tier(99)


def test_tier_prompt_injection():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = os.path.join(tmpdir, "tier_config.json")
        engine = SkillTierEngine(config_path=cfg)
        engine.set_active_tier(3)
        prompt = engine.get_prompt_injection()
        assert "ACTIVE OPERATIONAL SKILL TIER" in prompt
        assert "Tier 3" in prompt
        assert "FULL ACCESS" in prompt
