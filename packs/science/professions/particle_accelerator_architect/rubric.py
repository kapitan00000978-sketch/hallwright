"""100-Point Weighted Domain Rubric for Particle Accelerators & Relativistic Beam Dynamics.

Maintained by Dr. Julian 'The Accelerator' Vance.
Enforces betatron tune resonance avoidance, Courant-Snyder symplecticity,
superconducting cavity quench interlocks, and microsecond machine protection beam dumps.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .inspector import AcceleratorInspectionResult


@dataclass
class AcceleratorRubricEvaluation:
    """Quantitative scoring across 5 rigorous particle accelerator dimensions."""
    betatron_tune_score: float        # max 25.0
    relativistic_lorentz_score: float # max 20.0
    cavity_quench_score: float        # max 20.0
    machine_protection_score: float   # max 20.0
    code_determinism_score: float     # max 15.0
    total_score: float
    vetoed: bool
    veto_reasons: List[str] = field(default_factory=list)
    grade: str = "F"

    @property
    def passed(self) -> bool:
        return not self.vetoed and self.total_score >= 85.0

    def __iter__(self):
        """Allows unpacking as (score, breakdown, passed, veto_reason)."""
        yield self.total_score
        yield {
            "betatron_tune": self.betatron_tune_score,
            "relativistic_lorentz": self.relativistic_lorentz_score,
            "cavity_quench": self.cavity_quench_score,
            "machine_protection": self.machine_protection_score,
            "code_determinism": self.code_determinism_score,
        }
        yield self.passed
        yield " | ".join(self.veto_reasons)


class AcceleratorRubric:
    """Evaluates accelerator beam physics code against Dr. Julian Vance's 100-point standard."""

    PASSING_THRESHOLD: float = 85.0

    @classmethod
    def evaluate(cls, inspection_or_metrics: Any) -> AcceleratorRubricEvaluation:
        if isinstance(inspection_or_metrics, dict):
            inspection = AcceleratorInspectionResult(
                file_path="inline.py",
                syntax_valid=inspection_or_metrics.get("ast_valid", True),
                capabilities={
                    "has_relativistic_kinematics": inspection_or_metrics.get("has_relativistic_kinematics", False),
                    "has_tune_resonance_guard": inspection_or_metrics.get("has_tune_resonance_guard", False),
                    "has_cavity_quench_check": inspection_or_metrics.get("has_cavity_quench_check", False),
                    "has_telemetry_eval": inspection_or_metrics.get("has_telemetry_eval", False),
                    "has_kicker_dump_abort": inspection_or_metrics.get("has_kicker_dump_abort", False),
                },
                violations=inspection_or_metrics.get("violations", []),
                has_fatal_defects=inspection_or_metrics.get("has_fatal_defects", False),
                score=inspection_or_metrics.get("score", 0.0)
            )
        else:
            inspection = inspection_or_metrics

        veto_reasons: List[str] = []

        if not inspection.syntax_valid:
            return AcceleratorRubricEvaluation(
                betatron_tune_score=0.0,
                relativistic_lorentz_score=0.0,
                cavity_quench_score=0.0,
                machine_protection_score=0.0,
                code_determinism_score=0.0,
                total_score=0.0,
                vetoed=True,
                veto_reasons=["Syntax invalid: code cannot be parsed"],
                grade="F (SYNTAX ERROR)"
            )

        # 1. Betatron Tune Resonance Stability (25 points)
        tune_score = 0.0
        if inspection.capabilities.get("has_tune_resonance_guard"):
            tune_score += 25.0
        for v in inspection.violations:
            if "Substandard betatron tune" in v:
                tune_score = 0.0
                veto_reasons.append("VETO: Betatron tune margin below 0.05 provokes catastrophic beam emittance blow-up")

        # 2. Relativistic Lorentz Dynamics (20 points)
        lorentz_score = 0.0
        if inspection.capabilities.get("has_relativistic_kinematics"):
            lorentz_score += 20.0

        # 3. Superconducting RF Cavity Quench Interlocks (20 points)
        quench_score = 0.0
        if inspection.capabilities.get("has_cavity_quench_check"):
            quench_score += 20.0
        for v in inspection.violations:
            if "Superconducting RF cavity" in v:
                quench_score = max(0.0, quench_score - 15.0)
                veto_reasons.append("VETO: Cavity temperature exceeds 2.0K superfluid helium boundary")
            elif "Quench trip interlock" in v:
                quench_score = max(0.0, quench_score - 10.0)
                veto_reasons.append("Quench trip latency exceeds 10.0us threshold")

        # 4. Machine Protection & Fast Kicker Dump (20 points)
        mps_score = 0.0
        if inspection.capabilities.get("has_kicker_dump_abort"):
            mps_score += 20.0
        for v in inspection.violations:
            if "Kicker magnet abort latency" in v:
                mps_score = max(0.0, mps_score - 15.0)
                veto_reasons.append("Kicker dump latency exceeds 3.0us machine protection limit")

        # 5. Deterministic Code Quality (15 points)
        code_score = 15.0
        for v in inspection.violations:
            if "Lazy stub" in v or "Empty pass" in v:
                code_score = 0.0
                veto_reasons.append("VETO: Unfinished stub violates Hallwright zero-defect standard")

        total = tune_score + lorentz_score + quench_score + mps_score + code_score
        total = max(0.0, min(100.0, total))

        is_vetoed = len([r for r in veto_reasons if "VETO" in r]) > 0 or inspection.has_fatal_defects

        if is_vetoed:
            grade = "F (VETOED)"
        elif total >= 95.0:
            grade = "A+ (ACCELERATOR TITAN)"
        elif total >= 90.0:
            grade = "A (BEAM CERTIFIED)"
        elif total >= 85.0:
            grade = "B+ (PASS)"
        else:
            grade = "C (UNSAFE)"

        return AcceleratorRubricEvaluation(
            betatron_tune_score=tune_score,
            relativistic_lorentz_score=lorentz_score,
            cavity_quench_score=quench_score,
            machine_protection_score=mps_score,
            code_determinism_score=code_score,
            total_score=total,
            vetoed=is_vetoed,
            veto_reasons=veto_reasons,
            grade=grade
        )
