"""100-Point Weighted Domain Rubric for Subsea Autonomous Robotics & Deep-Sea Navigation.

Maintained by Commander Orion 'The Deep' Sterling.
Enforces structural hull collapse margins, Mackenzie acoustic models,
dielectric pressure compensation, and passive ballast jettison fail-safes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .inspector import DeepSeaInspectionResult


@dataclass
class DeepSeaRubricEvaluation:
    """Quantitative scoring across 5 rigorous subsea dimensions."""
    structural_crush_score: float     # max 25.0
    acoustic_navigation_score: float  # max 20.0
    dielectric_compensation_score: float # max 20.0
    buoyancy_ballast_score: float     # max 20.0
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
            "structural_crush": self.structural_crush_score,
            "acoustic_navigation": self.acoustic_navigation_score,
            "dielectric_compensation": self.dielectric_compensation_score,
            "buoyancy_ballast": self.buoyancy_ballast_score,
            "code_determinism": self.code_determinism_score,
        }
        yield self.passed
        yield " | ".join(self.veto_reasons)


class DeepSeaRubric:
    """Evaluates subsea robotics code against Commander Orion Sterling's 100-point standard."""

    PASSING_THRESHOLD: float = 85.0

    @classmethod
    def evaluate(cls, inspection_or_metrics: Any) -> DeepSeaRubricEvaluation:
        # Convert dict to DeepSeaInspectionResult if passed from inspect dict
        if isinstance(inspection_or_metrics, dict):
            inspection = DeepSeaInspectionResult(
                file_path="inline.py",
                syntax_valid=inspection_or_metrics.get("ast_valid", True),
                capabilities={
                    "has_hydrostatic_calc": inspection_or_metrics.get("has_hydrostatic_calc", False),
                    "has_sound_speed_model": inspection_or_metrics.get("has_sound_speed_model", False),
                    "has_hull_safety_check": inspection_or_metrics.get("has_hull_safety_check", False),
                    "has_telemetry_eval": inspection_or_metrics.get("has_telemetry_eval", False),
                    "has_passive_jettison": inspection_or_metrics.get("has_passive_jettison", False),
                },
                violations=inspection_or_metrics.get("violations", []),
                has_fatal_defects=inspection_or_metrics.get("has_fatal_defects", False),
                score=inspection_or_metrics.get("score", 0.0)
            )
        else:
            inspection = inspection_or_metrics

        veto_reasons: List[str] = []

        if not inspection.syntax_valid:
            return DeepSeaRubricEvaluation(
                structural_crush_score=0.0,
                acoustic_navigation_score=0.0,
                dielectric_compensation_score=0.0,
                buoyancy_ballast_score=0.0,
                code_determinism_score=0.0,
                total_score=0.0,
                vetoed=True,
                veto_reasons=["Syntax invalid: code cannot be parsed"],
                grade="F (SYNTAX ERROR)"
            )

        # 1. Structural Crush & Hull Collapse Safety (25 points)
        crush_score = 0.0
        if inspection.capabilities.get("has_hydrostatic_calc"):
            crush_score += 10.0
        if inspection.capabilities.get("has_hull_safety_check"):
            crush_score += 15.0
        for v in inspection.violations:
            if "Substandard hull collapse" in v:
                crush_score = 0.0
                veto_reasons.append("VETO: Hull collapse safety factor below 1.50 creates catastrophic implosion hazard")
            elif "Depth rating" in v:
                crush_score = max(0.0, crush_score - 10.0)
                veto_reasons.append("VETO: Depth rating below 11,000m fails Full Ocean Depth Challenger certification")

        # 2. Acoustic Navigation & Sound Velocity (20 points)
        acoustic_score = 0.0
        if inspection.capabilities.get("has_sound_speed_model"):
            acoustic_score += 15.0
        if inspection.capabilities.get("has_telemetry_eval"):
            acoustic_score += 5.0
        for v in inspection.violations:
            if "Acoustic position drift" in v:
                acoustic_score = max(0.0, acoustic_score - 10.0)
                veto_reasons.append("Acoustic dead-reckoning drift exceeds 2.0m threshold")

        # 3. Dielectric Pressure Compensation & Insulation (20 points)
        comp_score = 0.0
        if inspection.capabilities.get("has_telemetry_eval"):
            comp_score += 20.0
        for v in inspection.violations:
            if "Compensator reservoir bias" in v:
                comp_score = max(0.0, comp_score - 15.0)
                veto_reasons.append("VETO: Deficient compensator bias allows saline ingress into electronics")

        # 4. Buoyancy Trim & Passive Ballast Jettison (20 points)
        buoyancy_score = 0.0
        if inspection.capabilities.get("has_passive_jettison"):
            buoyancy_score += 20.0
        for v in inspection.violations:
            if "Emergency ballast drop time" in v:
                buoyancy_score = max(0.0, buoyancy_score - 15.0)
                veto_reasons.append("Emergency ballast drop exceeds 30.0s envelope")

        # 5. Deterministic Code Quality (15 points)
        code_score = 15.0
        for v in inspection.violations:
            if "Lazy stub" in v or "Empty pass" in v:
                code_score = 0.0
                veto_reasons.append("VETO: Unfinished stub violates Hallwright zero-defect standard")

        total = crush_score + acoustic_score + comp_score + buoyancy_score + code_score
        total = max(0.0, min(100.0, total))

        is_vetoed = len([r for r in veto_reasons if "VETO" in r]) > 0 or inspection.has_fatal_defects

        if is_vetoed:
            grade = "F (VETOED)"
        elif total >= 95.0:
            grade = "A+ (TITAN OF THE DEEP)"
        elif total >= 90.0:
            grade = "A (HADAL CERTIFIED)"
        elif total >= 85.0:
            grade = "B+ (PASS)"
        else:
            grade = "C (UNSAFE)"

        return DeepSeaRubricEvaluation(
            structural_crush_score=crush_score,
            acoustic_navigation_score=acoustic_score,
            dielectric_compensation_score=comp_score,
            buoyancy_ballast_score=buoyancy_score,
            code_determinism_score=code_score,
            total_score=total,
            vetoed=is_vetoed,
            veto_reasons=veto_reasons,
            grade=grade
        )
