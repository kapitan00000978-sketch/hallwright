"""100-Point Weighted Domain Rubric for Hypersonic Aerothermodynamics & Scramjet Propulsion.

Maintained by Dr. Zephyr 'The Hypersonic' Sterling.
Enforces scramjet isolator shock-train margins, Sutton-Graves aerothermal heating,
real-gas high-temperature dissociation, and sub-5ms unstart mitigation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .inspector import HypersonicInspectionResult


@dataclass
class HypersonicRubricEvaluation:
    """Quantitative scoring across 5 rigorous hypersonic aerothermodynamic dimensions."""
    isolator_stability_score: float   # max 25.0
    aerothermal_realgas_score: float  # max 20.0
    tps_material_score: float         # max 20.0
    unstart_mitigation_score: float   # max 20.0
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
            "isolator_stability": self.isolator_stability_score,
            "aerothermal_realgas": self.aerothermal_realgas_score,
            "tps_material": self.tps_material_score,
            "unstart_mitigation": self.unstart_mitigation_score,
            "code_determinism": self.code_determinism_score,
        }
        yield self.passed
        yield " | ".join(self.veto_reasons)


class HypersonicRubric:
    """Evaluates hypersonic propulsion and aerodynamics code against Dr. Zephyr Sterling's 100-point standard."""

    PASSING_THRESHOLD: float = 85.0

    @classmethod
    def evaluate(cls, inspection_or_metrics: Any) -> HypersonicRubricEvaluation:
        if isinstance(inspection_or_metrics, dict):
            inspection = HypersonicInspectionResult(
                file_path="inline.py",
                syntax_valid=inspection_or_metrics.get("ast_valid", True),
                capabilities={
                    "has_aerothermal_heating": inspection_or_metrics.get("has_aerothermal_heating", False),
                    "has_real_gas_model": inspection_or_metrics.get("has_real_gas_model", False),
                    "has_isolator_stability": inspection_or_metrics.get("has_isolator_stability", False),
                    "has_telemetry_eval": inspection_or_metrics.get("has_telemetry_eval", False),
                    "has_unstart_mitigation": inspection_or_metrics.get("has_unstart_mitigation", False),
                },
                violations=inspection_or_metrics.get("violations", []),
                has_fatal_defects=inspection_or_metrics.get("has_fatal_defects", False),
                score=inspection_or_metrics.get("score", 0.0)
            )
        else:
            inspection = inspection_or_metrics

        veto_reasons: List[str] = []

        if not inspection.syntax_valid:
            return HypersonicRubricEvaluation(
                isolator_stability_score=0.0,
                aerothermal_realgas_score=0.0,
                tps_material_score=0.0,
                unstart_mitigation_score=0.0,
                code_determinism_score=0.0,
                total_score=0.0,
                vetoed=True,
                veto_reasons=["Syntax invalid: code cannot be parsed"],
                grade="F (SYNTAX ERROR)"
            )

        # 1. Scramjet Isolator Shock Train Stability (25 points)
        iso_score = 0.0
        if inspection.capabilities.get("has_isolator_stability"):
            iso_score += 25.0
        for v in inspection.violations:
            if "Substandard scramjet isolator" in v:
                iso_score = 0.0
                veto_reasons.append("VETO: Scramjet isolator margin below 1.25 provokes catastrophic inlet unstart")

        # 2. Aerothermal Stagnation Heating & Real-Gas (20 points)
        aero_score = 0.0
        if inspection.capabilities.get("has_aerothermal_heating"):
            aero_score += 10.0
        if inspection.capabilities.get("has_real_gas_model"):
            aero_score += 10.0

        # 3. Thermal Protection System & Material Limits (20 points)
        tps_score = 0.0
        if inspection.capabilities.get("has_telemetry_eval"):
            tps_score += 20.0
        for v in inspection.violations:
            if "Substandard Thermal Protection" in v:
                tps_score = max(0.0, tps_score - 15.0)
                veto_reasons.append("VETO: TPS safety factor below 1.50 risks leading-edge thermal burn-through")

        # 4. Active Unstart Mitigation & Fuel Throttle (20 points)
        unstart_score = 0.0
        if inspection.capabilities.get("has_unstart_mitigation"):
            unstart_score += 20.0
        for v in inspection.violations:
            if "Unstart mitigation response latency" in v:
                unstart_score = max(0.0, unstart_score - 15.0)
                veto_reasons.append("Unstart mitigation latency exceeds 5.0ms dynamic shock limit")

        # 5. Deterministic Code Quality (15 points)
        code_score = 15.0
        for v in inspection.violations:
            if "Lazy stub" in v or "Empty pass" in v:
                code_score = 0.0
                veto_reasons.append("VETO: Unfinished stub violates Hallwright zero-defect standard")

        total = iso_score + aero_score + tps_score + unstart_score + code_score
        total = max(0.0, min(100.0, total))

        is_vetoed = len([r for r in veto_reasons if "VETO" in r]) > 0 or inspection.has_fatal_defects

        if is_vetoed:
            grade = "F (VETOED)"
        elif total >= 95.0:
            grade = "A+ (HYPERSONIC TITAN)"
        elif total >= 90.0:
            grade = "A (SCRAMJET CERTIFIED)"
        elif total >= 85.0:
            grade = "B+ (PASS)"
        else:
            grade = "C (UNSAFE)"

        return HypersonicRubricEvaluation(
            isolator_stability_score=iso_score,
            aerothermal_realgas_score=aero_score,
            tps_material_score=tps_score,
            unstart_mitigation_score=unstart_score,
            code_determinism_score=code_score,
            total_score=total,
            vetoed=is_vetoed,
            veto_reasons=veto_reasons,
            grade=grade
        )
