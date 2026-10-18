"""⚡ DR. SILAS 'THE PLASMA' VANCE — FUSION PLASMA ARCHITECT
Autonomous tokamak physics audit, Kruskal-Shafranov stability verification,
Greenwald density limit defense, and NTM island suppression elevation engine.

Usage:
    python professions/fusion_plasma_architect/master.py <code_file> [--elevate]
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception as _enc_err:
        sys.stderr.write(f"Note: UTF-8 stdout reconfiguration skipped: {_enc_err}\n")

try:
    from .references import FusionReferenceLibrary
    from .inspector import FusionPlasmaInspector
    from .rubric import FusionPlasmaRubric
    from .blind_critic import FusionPlasmaBlindCritic
    from .elevation_engine import FusionPlasmaElevationEngine
except ImportError:
    from references import FusionReferenceLibrary
    from inspector import FusionPlasmaInspector
    from rubric import FusionPlasmaRubric
    from blind_critic import FusionPlasmaBlindCritic
    from elevation_engine import FusionPlasmaElevationEngine

# Import global ActiveDecisionJournal from studio engine
try:
    from src.studio.active_memory import ActiveDecisionJournal
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.studio.active_memory import ActiveDecisionJournal


class SilasVanceMaster:
    """Dr. Silas Vance: The living tokamak magnetic confinement & fusion plasma sovereign.
    Guarantees edge safety factor q95 >= 3.0, Troyon normalized beta <= 3.5,
    Greenwald density fraction <= 0.85, NTM microwave ECCD suppression, and divertor heat flux limits.
    """

    def __init__(
        self,
        target_path: Optional[str] = None,
        passing_threshold: int = 85,
        max_cycles: int = 3,
    ):
        self.target_path = os.path.abspath(target_path) if target_path else None
        self.passing_threshold = passing_threshold
        self.max_cycles = max_cycles
        self.inspector = FusionPlasmaInspector()
        self.rubric = FusionPlasmaRubric()
        self.critic = FusionPlasmaBlindCritic()
        self.elevation_engine = FusionPlasmaElevationEngine()
        self.journal = ActiveDecisionJournal()

    def run_autonomous_cycle(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """Executes the closed-loop autonomous tokamak stability audit & elevation lifecycle.
        1. Inspect -> 2. Rubric -> 3. Critic -> 4. Elevate (if < 85) -> 5. Certify & Journal
        """
        data = input_data
        if data is None and self.target_path:
            if os.path.exists(self.target_path):
                with open(self.target_path, "r", encoding="utf-8") as f:
                    data = f.read()
            else:
                raise FileNotFoundError(f"Target tokamak plasma file not found: {self.target_path}")

        if data is None:
            data = FusionReferenceLibrary.get_canonical_core()

        current_data = data
        initial_critique = self.critic.evaluate(current_data)
        cycles_performed = 0

        # Elevation cycle if below passing threshold
        if not initial_critique["passed"] or initial_critique["fatal_defects_count"] > 0:
            elevation_result = self.elevation_engine.elevate(
                current_data, target_score=self.passing_threshold, max_iterations=self.max_cycles
            )
            current_data = elevation_result["elevated_code"]
            cycles_performed = elevation_result.get("iterations", 0)

        # Final audit
        final_critique = self.critic.evaluate(current_data)
        is_certified = final_critique["passed"] and (final_critique["fatal_defects_count"] == 0)

        # Record decision in persistent Hallwright journal
        self._record_journal_entry(
            initial_score=initial_critique["score"],
            final_score=final_critique["score"],
            fatal_defects=final_critique["fatal_defects_count"],
        )

        briefing = self._generate_briefing(current_data, final_critique, is_certified)

        # Overwrite file if target path was supplied and code was elevated
        if self.target_path and cycles_performed > 0:
            try:
                with open(self.target_path, "w", encoding="utf-8") as f:
                    f.write(current_data)
            except Exception as _write_err:
                sys.stderr.write(f"Note: Could not overwrite target tokamak file: {_write_err}\n")

        return {
            "status": "CERTIFIED" if is_certified else "REJECTED",
            "initial_score": initial_critique["score"],
            "final_score": final_critique["score"],
            "is_certified": is_certified,
            "cycles_performed": cycles_performed,
            "verdict": final_critique["verdict"],
            "fatal_defects_count": final_critique["fatal_defects_count"],
            "defects": final_critique["defect_ledger"],
            "elevated_code": current_data,
            "executive_briefing": briefing,
        }

    def _record_journal_entry(
        self,
        initial_score: int,
        final_score: int,
        fatal_defects: int,
    ) -> None:
        try:
            self.journal.record_decision(
                iteration=1,
                target_file=self.target_path if self.target_path else "tokamak_plasma_controller.py",
                defects_before=[f"Fatal defects: {fatal_defects}"],
                actions_taken=["silas_vance_fusion_plasma_elevation"],
                score_before=float(initial_score),
                score_after=float(final_score),
            )
        except Exception as _journal_err:
            sys.stderr.write(f"Note: Decision journal record skipped: {_journal_err}\n")

    def _generate_briefing(self, code_data: str, critique: Dict[str, Any], is_certified: bool) -> str:
        metrics = self.inspector.inspect(code_data)
        status_icon = "⚡ [MHD PLASMA STABILITY CERTIFIED]" if is_certified else "⚠️ [REJECTED TOKAMAK DISRUPTION HAZARD]"

        briefing = [
            f"# {status_icon} EXECUTIVE FUSION PLASMA BRIEFING",
            "**Auditor:** Dr. Silas 'The Plasma' Vance (Principal Tokamak Plasma Architect)",
            f"**Final Score:** {critique['score']}/100 (Threshold: {self.passing_threshold})",
            f"**Verdict:** {critique['verdict']}",
            "",
            "## 1. Tokamak Magnetic Confinement & MHD Invariants",
            f"- **Edge Safety Factor q95:** {'PASS (q95 >= 3.0 Kruskal-Shafranov Safe)' if metrics.get('q95_safe') else 'FAIL (Kink Disruption Risk)'}",
            f"- **Troyon Normalized Beta:** {'PASS (beta_N <= 3.5 Ideal MHD Bounded)' if metrics.get('has_troyon_beta_logic') else 'FAIL (Ballooning Instability Risk)'}",
            f"- **Greenwald Density Fraction:** {'PASS (f_G <= 0.85 Below Radiative Collapse)' if metrics.get('density_safe') else 'FAIL (Density Limit Disruption)'}",
            f"- **NTM Tearing Mode Suppression:** {'PASS (Resonant Microwave ECCD Active)' if metrics.get('has_ntm_stabilization') else 'WARN (Locked Mode Hazard)'}",
            f"- **Divertor Peak Heat Exhaust:** {'PASS (<= 10 MW/m^2 Tungsten Safe)' if metrics.get('has_divertor_protection') else 'WARN (Divertor Melting Risk)'}",
            "",
            "## 2. Defect Ledger & Elevation Actions",
        ]

        if critique["defect_ledger"]:
            for d in critique["defect_ledger"]:
                briefing.append(f"- **[{d['severity']}] {d['rule']}:** {d['description']}")
                briefing.append(f"  *Remediation:* {d['remediation']}")
        else:
            briefing.append("✅ Zero disruption precursors or MHD instabilities detected. Plasma equilibrium certified for burning plasma discharge.")

        return "\n".join(briefing)


def main():
    parser = argparse.ArgumentParser(description="Dr. Silas Vance Autonomous Fusion Plasma Master")
    parser.add_argument("target", nargs="?", help="Path to tokamak plasma control code file")
    parser.add_argument("--elevate", action="store_true", help="Auto-elevate flawed fusion code to 100/100 score")
    args = parser.parse_args()

    master = SilasVanceMaster(target_path=args.target)
    result = master.run_autonomous_cycle()

    print(result["executive_briefing"])
    sys.exit(0 if result["is_certified"] else 1)


if __name__ == "__main__":
    main()
