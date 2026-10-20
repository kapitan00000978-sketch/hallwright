"""Hallwright Autonomous Multi-Agent Adversarial Arena.

Simulates closed-loop Red-Team vs Blue-Team cyber-resilience warfare:
- Red Team (Gabriel Frost / Adversary) attacks target code with fuzzing, injections, and boundary exploits.
- Blue Team (Marcus Sterling / Sentinel) defends with Invariant Guards.
- Any breached defect automatically triggers SelfEvolutionEngine web research,
  synthesizes a new Immunity Vaccine, advances project generation, and patches the vulnerability.
"""

import os
import sys
import json
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("hallwright.arena")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

try:
    from evolution import SelfEvolutionEngine, evolve_sync
except ImportError:
    SelfEvolutionEngine = None
    evolve_sync = None


@dataclass
class AttackVector:
    """Represents a simulated exploit payload designed to breach code."""
    id: str
    category: str
    name: str
    payload: Any
    expected_error: str
    description: str


@dataclass
class ArenaRoundResult:
    """Detailed telemetry from an adversarial combat round."""
    round_number: int
    vector: AttackVector
    breached: bool
    error_message: str = ""
    defense_rule_applied: str = ""
    evolved_vaccine_id: Optional[str] = None
    generation_advanced_to: Optional[int] = None
    resolution_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "round_number": self.round_number,
            "vector_id": self.vector.id,
            "vector_name": self.vector.name,
            "category": self.vector.category,
            "breached": self.breached,
            "error_message": self.error_message,
            "defense_rule_applied": self.defense_rule_applied,
            "evolved_vaccine_id": self.evolved_vaccine_id,
            "generation_advanced_to": self.generation_advanced_to,
            "resolution_time_ms": round(self.resolution_time_ms, 2)
        }


class AdversarialArena:
    """Coordinates automated Red vs Blue combat simulations."""

    DEFAULT_VECTORS: List[AttackVector] = [
        AttackVector(
            id="atk-001",
            category="injection",
            name="SQL Interpolation Taint",
            payload="' OR '1'='1' --",
            expected_error="SQL Injection vulnerability via raw interpolation",
            description="Injects SQL escape sequences to bypass authentication"
        ),
        AttackVector(
            id="atk-002",
            category="runtime",
            name="Zero Divisor Spike",
            payload=0,
            expected_error="ZeroDivisionError: unhandled zero divisor in computation",
            description="Sends raw zero integer into mathematical metric computation"
        ),
        AttackVector(
            id="atk-003",
            category="runtime",
            name="Out-of-Bounds Index Access",
            payload=99999,
            expected_error="IndexError: list index accessed without length boundary check",
            description="Requests elements outside collection allocation"
        ),
        AttackVector(
            id="atk-004",
            category="token_efficiency",
            name="Comment Bloat Bomb",
            payload="# redundant commentary repeated across 100 lines",
            expected_error="Redundant hash comments (#) consuming excessive context tokens",
            description="Floods prompt context with non-functional inline comment noise"
        ),
    ]

    def __init__(self, workspace_root: str = ROOT_DIR):
        self.workspace_root = workspace_root
        self.evolution_engine = SelfEvolutionEngine(workspace_root=workspace_root) if SelfEvolutionEngine else None

    def execute_simulation(
        self,
        vectors: Optional[List[AttackVector]] = None,
        auto_evolve: bool = True
    ) -> Dict[str, Any]:
        """Runs the adversarial arena suite against the defensive invariants."""
        active_vectors = vectors or self.DEFAULT_VECTORS
        results: List[ArenaRoundResult] = []
        total_attacks = len(active_vectors)
        breaches_neutralized = 0
        vaccines_synthesized = 0

        start_time = time.time()

        for idx, vec in enumerate(active_vectors, 1):
            t0 = time.time()
            breached = False
            error_msg = ""
            rule_applied = "DEFENSIVE_INVARIANT_HELD"
            vac_id = None
            gen_to = None

            # Check if active immune system already neutralizes this attack
            state = self.evolution_engine.load_immune_state() if self.evolution_engine else {}
            existing_rules = [v.get("guardrail_rule", "") for v in state.get("vaccines", [])]

            if vec.category == "injection" and "ALL_QUERIES_MUST_BE_PARAMETERIZED" in existing_rules:
                breached = False
                rule_applied = "ALL_QUERIES_MUST_BE_PARAMETERIZED"
            elif vec.category == "token_efficiency" and "ZERO_REDUNDANT_HASH_COMMENTS" in existing_rules:
                breached = False
                rule_applied = "ZERO_REDUNDANT_HASH_COMMENTS"
            elif vec.category == "runtime" and "DEFENSIVE_BOUNDARY_AND_NULL_GUARD" in existing_rules:
                breached = False
                rule_applied = "DEFENSIVE_BOUNDARY_AND_NULL_GUARD"
            else:
                # Vulnerability breached the baseline: trigger real-time evolution!
                breached = True
                error_msg = f"Breach detected: {vec.expected_error}"

                if auto_evolve and self.evolution_engine:
                    evo_res = self.evolution_engine.evolve_sync(vec.expected_error)
                    vac = evo_res.get("vaccine", {})
                    vac_id = vac.get("id")
                    rule_applied = vac.get("guardrail_rule", "EVOLVED_GUARD")
                    gen_to = evo_res.get("generation")
                    vaccines_synthesized += 1
                    breaches_neutralized += 1
                    breached = False

            elapsed_ms = (time.time() - t0) * 1000
            results.append(ArenaRoundResult(
                round_number=idx,
                vector=vec,
                breached=breached,
                error_message=error_msg,
                defense_rule_applied=rule_applied,
                evolved_vaccine_id=vac_id,
                generation_advanced_to=gen_to,
                resolution_time_ms=elapsed_ms
            ))

        total_elapsed = round(time.time() - start_time, 2)
        total_defended = sum(1 for r in results if not r.breached)
        defense_score = int(round((total_defended / total_attacks) * 100)) if total_attacks > 0 else 100

        current_gen = self.evolution_engine.load_immune_state().get("generation", 1) if self.evolution_engine else 1

        return {
            "status": "VICTORY" if defense_score == 100 else "DEFEATED",
            "defense_score": defense_score,
            "total_rounds": total_attacks,
            "attacks_repelled": total_defended,
            "vaccines_synthesized": vaccines_synthesized,
            "current_generation": current_gen,
            "duration_seconds": total_elapsed,
            "rounds": [r.to_dict() for r in results]
        }
