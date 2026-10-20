"""Hallwright Operational Skill Tiers & Access Control Engine.

Defines the 3 Skill Tiers governing AI agent authority and project access:
- Tier 1: Sentinel Advisory (Read-only, static security audits, inspection)
- Tier 2: Craftsman Artisan (Collaborative builder, defensive code generation)
- Tier 3: Sovereign Titan (FULL ACCESS - Maximum project power, 11-Titan swarm,
  live web healing, closed-loop immune evolution, and token compression).
"""

import os
import sys
import json
import logging
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

logger = logging.getLogger("hallwright.tiers")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TIER_CONFIG_PATH = os.path.join(ROOT_DIR, ".hallwright", "tier_config.json")


class TierLevel(IntEnum):
    TIER_1_SENTINEL = 1
    TIER_2_ARTISAN = 2
    TIER_3_SOVEREIGN = 3


@dataclass
class AccessPolicy:
    """Defines capabilities, authority, and invariants for a skill tier."""
    tier: int
    name: str
    uzbek_title: str
    description: str
    full_access: bool
    can_modify_files: bool
    can_execute_swarm: bool
    can_evolve_immune_system: bool
    can_run_web_healer: bool
    can_compress_tokens: bool
    can_run_daemon: bool
    prompt_directive: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier,
            "name": self.name,
            "uzbek_title": self.uzbek_title,
            "description": self.description,
            "full_access": self.full_access,
            "can_modify_files": self.can_modify_files,
            "can_execute_swarm": self.can_execute_swarm,
            "can_evolve_immune_system": self.can_evolve_immune_system,
            "can_run_web_healer": self.can_run_web_healer,
            "can_compress_tokens": self.can_compress_tokens,
            "can_run_daemon": self.can_run_daemon,
            "prompt_directive": self.prompt_directive
        }


TIER_POLICIES: Dict[int, AccessPolicy] = {
    TierLevel.TIER_1_SENTINEL: AccessPolicy(
        tier=1,
        name="Sentinel Advisory",
        uzbek_title="1-Daraja: Kuzatuv va Maslahat (Xavfsiz Rejim)",
        description="Read-only analysis, static AST security audits, flaw detection, and architectural recommendations.",
        full_access=False,
        can_modify_files=False,
        can_execute_swarm=False,
        can_evolve_immune_system=False,
        can_run_web_healer=False,
        can_compress_tokens=False,
        can_run_daemon=False,
        prompt_directive="OPERATIONAL TIER 1 (SENTINEL ADVISORY): Operate in read-only advisory mode. Do not write or overwrite files directly. Provide diagnoses, code diff suggestions, and audit findings."
    ),
    TierLevel.TIER_2_ARTISAN: AccessPolicy(
        tier=2,
        name="Craftsman Artisan",
        uzbek_title="2-Daraja: Faol Quruvchi (Standart Rejim)",
        description="Standard collaborative craftsman builder. Writes clean code, enforces 100/100 Gatekeeper benchmarks, and strips comment bloat.",
        full_access=False,
        can_modify_files=True,
        can_execute_swarm=False,
        can_evolve_immune_system=True,
        can_run_web_healer=True,
        can_compress_tokens=True,
        can_run_daemon=False,
        prompt_directive="OPERATIONAL TIER 2 (CRAFTSMAN ARTISAN): Operate as a collaborative software craftsman. Deliver production-ready code with zero stubs, verified 100/100 Gatekeeper score, and defensive guards."
    ),
    TierLevel.TIER_3_SOVEREIGN: AccessPolicy(
        tier=3,
        name="Sovereign Sovereign (Titan Overdrive)",
        uzbek_title="3-Daraja: To'liq Erkinlik & Maksimal Quvvat (FULL ACCESS)",
        description="FULL ACCESS & MAXIMUM PROJECT UTILIZATION. Autonomous 11-Titan swarm orchestration, non-blocking web healing, closed-loop immune evolution, and token compression with zero babysitting.",
        full_access=True,
        can_modify_files=True,
        can_execute_swarm=True,
        can_evolve_immune_system=True,
        can_run_web_healer=True,
        can_compress_tokens=True,
        can_run_daemon=True,
        prompt_directive=(
            "OPERATIONAL TIER 3 (FULL ACCESS & MAXIMUM PROJECT UTILIZATION):\n"
            "You possess unrestricted sovereign authority across all Hallwright subsystems. "
            "Autonomously orchestrate the 11-Titan Swarm, execute closed-loop self-evolution, "
            "trigger background web-healing without halting, minify token bloat, and deliver zero-defect results with zero babysitting."
        )
    ),
}


class SkillTierEngine:
    """Manages active tier state, authority checks, and prompt injections."""

    def __init__(self, config_path: str = TIER_CONFIG_PATH):
        self.config_path = config_path

    def get_active_tier(self) -> AccessPolicy:
        """Retrieves currently configured skill tier (defaults to Tier 3 Full Access)."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                tier_val = int(data.get("tier", TierLevel.TIER_3_SOVEREIGN))
                return TIER_POLICIES.get(tier_val, TIER_POLICIES[TierLevel.TIER_3_SOVEREIGN])
            except Exception as read_err:
                logger.debug("Failed reading tier config: %s", read_err)
        # Default is Tier 3 Full Access
        return TIER_POLICIES[TierLevel.TIER_3_SOVEREIGN]

    def set_active_tier(self, tier: int) -> AccessPolicy:
        """Sets and persists the active skill tier."""
        if tier not in (1, 2, 3):
            raise ValueError(f"Invalid tier {tier}. Valid tiers are 1, 2, or 3.")

        policy = TIER_POLICIES[tier]
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({
                    "tier": policy.tier,
                    "name": policy.name,
                    "uzbek_title": policy.uzbek_title,
                    "full_access": policy.full_access,
                    "description": policy.description
                }, f, indent=2)
        except OSError as write_err:
            logger.debug("Failed persisting tier config: %s", write_err)

        return policy

    def get_prompt_injection(self) -> str:
        """Returns systemic prompt injection for the active tier."""
        policy = self.get_active_tier()
        return (
            f"## ⚡ ACTIVE OPERATIONAL SKILL TIER: {policy.name} (Tier {policy.tier})\n"
            f"**Authority:** {'🔥 FULL ACCESS (Maximum Project Power)' if policy.full_access else '🛡️ Controlled Mode'}\n"
            f"**Directive:** {policy.prompt_directive}\n"
        )
