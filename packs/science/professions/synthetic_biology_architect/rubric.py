"""100-Point Weighted Domain Rubric for Synthetic Biology & Metabolic Genetic Circuits.

Maintained by Dr. Seraphiel 'The SynBio' Sterling.
Enforces multi-layer biocontainment escape frequencies, Hill cooperativity,
metabolic burden constraints, and orthogonal transcriptional regulation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .inspector import SynBioInspectionResult


@dataclass
class SynBioRubricEvaluation:
    """Quantitative scoring across 5 rigorous synthetic biology dimensions."""
    biocontainment_score: float      # max 25.0
    hill_kinetics_score: float       # max 20.0
    metabolic_burden_score: float    # max 20.0
    orthogonality_score: float       # max 20.0
    code_determinism_score: float    # max 15.0
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
            "biocontainment": self.biocontainment_score,
            "hill_kinetics": self.hill_kinetics_score,
            "metabolic_burden": self.metabolic_burden_score,
            "orthogonality": self.orthogonality_score,
            "code_determinism": self.code_determinism_score,
        }
        yield self.passed
        yield " | ".join(self.veto_reasons)


class SynBioRubric:
    """Evaluates synthetic biology code against Dr. Seraphiel Sterling's 100-point standard."""

    PASSING_THRESHOLD: float = 85.0

    @classmethod
    def evaluate(cls, inspection_or_metrics: Any) -> SynBioRubricEvaluation:
        if isinstance(inspection_or_metrics, dict):
            inspection = SynBioInspectionResult(
                file_path="inline.py",
                syntax_valid=inspection_or_metrics.get("ast_valid", True),
                capabilities={
                    "has_hill_kinetics": inspection_or_metrics.get("has_hill_kinetics", False),
                    "has_metabolic_burden_calc": inspection_or_metrics.get("has_metabolic_burden_calc", False),
                    "has_crosstalk_check": inspection_or_metrics.get("has_crosstalk_check", False),
                    "has_telemetry_eval": inspection_or_metrics.get("has_telemetry_eval", False),
                    "has_suicide_kill_switch": inspection_or_metrics.get("has_suicide_kill_switch", False),
                },
                violations=inspection_or_metrics.get("violations", []),
                has_fatal_defects=inspection_or_metrics.get("has_fatal_defects", False),
                score=inspection_or_metrics.get("score", 0.0)
            )
        else:
            inspection = inspection_or_metrics

        veto_reasons: List[str] = []

        if not inspection.syntax_valid:
            return SynBioRubricEvaluation(
                biocontainment_score=0.0,
                hill_kinetics_score=0.0,
                metabolic_burden_score=0.0,
                orthogonality_score=0.0,
                code_determinism_score=0.0,
                total_score=0.0,
                vetoed=True,
                veto_reasons=["Syntax invalid: code cannot be parsed"],
                grade="F (SYNTAX ERROR)"
            )

        # 1. Biocontainment & Kill Switch Safety (25 points)
        bio_score = 0.0
        if inspection.capabilities.get("has_suicide_kill_switch"):
            bio_score += 25.0
        for v in inspection.violations:
            if "Biocontainment escape frequency" in v:
                bio_score = 0.0
                veto_reasons.append("VETO: Escape frequency exceeds 1.0e-8 NIH biocontainment threshold")
            elif "Kill switch activation latency" in v:
                bio_score = max(0.0, bio_score - 10.0)
                veto_reasons.append("Kill switch activation latency exceeds 60.0 min limit")

        # 2. Hill Cooperativity & Transfer Functions (20 points)
        hill_score = 0.0
        if inspection.capabilities.get("has_hill_kinetics"):
            hill_score += 20.0
        for v in inspection.violations:
            if "Substandard Hill cooperativity" in v:
                hill_score = max(0.0, hill_score - 15.0)
                veto_reasons.append("Hill cooperativity n < 2.0 fails discrete bistable switching")

        # 3. Cellular Metabolic Burden Budget (20 points)
        burden_score = 0.0
        if inspection.capabilities.get("has_metabolic_burden_calc"):
            burden_score += 20.0
        for v in inspection.violations:
            if "Metabolic burden limit" in v:
                burden_score = max(0.0, burden_score - 15.0)
                veto_reasons.append("VETO: Metabolic burden exceeds 30% host cellular translation budget")

        # 4. Orthogonal Transcriptional Isolation (20 points)
        ortho_score = 0.0
        if inspection.capabilities.get("has_crosstalk_check"):
            ortho_score += 15.0
        if inspection.capabilities.get("has_telemetry_eval"):
            ortho_score += 5.0

        # 5. Deterministic Code Quality (15 points)
        code_score = 15.0
        for v in inspection.violations:
            if "Lazy stub" in v or "Empty pass" in v:
                code_score = 0.0
                veto_reasons.append("VETO: Unfinished stub violates Hallwright zero-defect standard")

        total = bio_score + hill_score + burden_score + ortho_score + code_score
        total = max(0.0, min(100.0, total))

        is_vetoed = len([r for r in veto_reasons if "VETO" in r]) > 0 or inspection.has_fatal_defects

        if is_vetoed:
            grade = "F (VETOED)"
        elif total >= 95.0:
            grade = "A+ (SYNTHETIC BIOLOGY TITAN)"
        elif total >= 90.0:
            grade = "A (GENOMIC CIRCUIT CERTIFIED)"
        elif total >= 85.0:
            grade = "B+ (PASS)"
        else:
            grade = "C (UNSAFE)"

        return SynBioRubricEvaluation(
            biocontainment_score=bio_score,
            hill_kinetics_score=hill_score,
            metabolic_burden_score=burden_score,
            orthogonality_score=ortho_score,
            code_determinism_score=code_score,
            total_score=total,
            vetoed=is_vetoed,
            veto_reasons=veto_reasons,
            grade=grade
        )
