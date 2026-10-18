"""⚡ DR. JULIAN 'THE ACCELERATOR' VANCE — PARTICLE ACCELERATOR ARCHITECT
Autonomous relativistic beam dynamics audit, betatron tune resonance avoidance,
superconducting cavity quench interlocks, and machine protection elevation engine.

Usage:
    python professions/particle_accelerator_architect/master.py <code_file> [--elevate]
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
    from .references import AcceleratorReferenceLibrary
    from .inspector import AcceleratorInspector
    from .rubric import AcceleratorRubric
    from .blind_critic import AcceleratorBlindCritic
    from .elevation_engine import AcceleratorElevationEngine
except ImportError:
    from references import AcceleratorReferenceLibrary
    from inspector import AcceleratorInspector
    from rubric import AcceleratorRubric
    from blind_critic import AcceleratorBlindCritic
    from elevation_engine import AcceleratorElevationEngine

# Import global ActiveDecisionJournal from studio engine
try:
    from src.studio.active_memory import ActiveDecisionJournal
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.studio.active_memory import ActiveDecisionJournal


class JulianVanceMaster:
    """Dr. Julian 'The Accelerator' Vance: The living particle accelerator & beam physics sovereign.
    Guarantees relativistic Lorentz kinematics (gamma >= 100), betatron tune resonance margin >= 0.05,
    superconducting cavity temperature <= 2.0K, sub-10us quench trip, and sub-3us kicker dump abort.
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
        self.inspector = AcceleratorInspector()
        self.rubric = AcceleratorRubric()
        self.critic = AcceleratorBlindCritic()
        self.elevation_engine = AcceleratorElevationEngine()
        self.journal = ActiveDecisionJournal()

    def run_autonomous_cycle(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """Executes the closed-loop autonomous accelerator stability audit & elevation lifecycle.
        1. Inspect -> 2. Rubric -> 3. Critic -> 4. Elevate (if < 85) -> 5. Certify & Journal
        """
        data = input_data
        if data is None and self.target_path:
            if os.path.exists(self.target_path):
                with open(self.target_path, "r", encoding="utf-8") as f:
                    data = f.read()
            else:
                raise FileNotFoundError(f"Target accelerator file not found: {self.target_path}")

        if data is None:
            data = AcceleratorReferenceLibrary.get_canonical_core()

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
                sys.stderr.write(f"Note: Could not overwrite target accelerator file: {_write_err}\n")

        return {
            "status": "CERTIFIED" if is_certified else "REJECTED",
            "initial_score": initial_critique["score"],
            "final_score": final_critique["score"],
            "is_certified": is_certified,
            "cycles_performed": cycles_performed,
            "verdict": "APPROVED" if is_certified else final_critique["verdict"],
            "fatal_defects_count": final_critique["fatal_defects_count"],
            "defects": final_critique["defect_ledger"],
            "elevated_code": current_data,
            "executive_briefing": briefing,
        }

    def _record_journal_entry(
        self,
        initial_score: float,
        final_score: float,
        fatal_defects: int,
    ) -> None:
        try:
            self.journal.record_decision(
                iteration=1,
                target_file=self.target_path if self.target_path else "particle_beam_executive.py",
                defects_before=[f"Fatal defects: {fatal_defects}"],
                actions_taken=["julian_vance_accelerator_beam_elevation"],
                score_before=float(initial_score),
                score_after=float(final_score),
            )
        except Exception as _journal_err:
            sys.stderr.write(f"Note: Could not record in ActiveDecisionJournal: {_journal_err}\n")

    def _generate_briefing(
        self,
        code: str,
        critique: Dict[str, Any],
        is_certified: bool,
    ) -> str:
        lines = [
            "=" * 78,
            "⚡ DR. JULIAN VANCE — EXECUTIVE PARTICLE ACCELERATOR BRIEFING",
            "=" * 78,
            f"Certification Status : {'CERTIFIED' if is_certified else 'REJECTED'}",
            f"Final Safety Score   : {critique['score']:.1f}/100 [{critique['grade']}]",
            f"Fatal Beam Defects   : {critique['fatal_defects_count']}",
            f"Machine Warnings     : {critique['warnings_count']}",
            "-" * 78,
            "Particle Accelerator & Relativistic Invariants Enforced:",
            "  1. Lorentz Factor Compliance     : gamma >= 100.0 (ultra-relativistic v approx c)",
            "  2. Betatron Tune Resonance Margin: delta_nu >= 0.05 isolation from stopbands",
            "  3. Courant-Snyder Symplecticity  : beta * gamma - alpha^2 == 1 phase space area",
            "  4. Superconducting RF Cryogenics : T_cavity <= 2.0K (superfluid liquid helium)",
            "  5. Fast Quench Interlock Latency : t_quench <= 10.0us fast RF trip",
            "  6. Machine Protection Beam Dump  : t_kicker <= 3.0us extraction into beam absorber",
            "=" * 78,
        ]
        return "\n".join(lines)


# Convenient Alias
AcceleratorMaster = JulianVanceMaster


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dr. Julian Vance Particle Accelerator & Beam Physics Master"
    )
    parser.add_argument("file", nargs="?", default=None, help="Path to Python accelerator file to audit")
    parser.add_argument("--elevate", action="store_true", help="Autonomously elevate flawed accelerator code")
    parser.add_argument("--threshold", type=int, default=85, help="Passing safety score threshold")
    args = parser.parse_args()

    master = JulianVanceMaster(target_path=args.file, passing_threshold=args.threshold)
    result = master.run_autonomous_cycle()

    print(result["executive_briefing"])
    sys.exit(0 if result["is_certified"] else 1)


if __name__ == "__main__":
    main()
