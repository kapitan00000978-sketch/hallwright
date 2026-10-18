"""⚡ DR. ZEPHYR 'THE HYPERSONIC' STERLING — HYPERSONIC AERODYNAMICS ARCHITECT
Autonomous hypersonic aerothermodynamics audit, Sutton-Graves stagnation heating verification,
scramjet isolator unstart defense, and UHTC thermal protection elevation engine.

Usage:
    python professions/hypersonic_aerodynamics_architect/master.py <code_file> [--elevate]
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
    from .references import HypersonicReferenceLibrary
    from .inspector import HypersonicInspector
    from .rubric import HypersonicRubric
    from .blind_critic import HypersonicBlindCritic
    from .elevation_engine import HypersonicElevationEngine
except ImportError:
    from references import HypersonicReferenceLibrary
    from inspector import HypersonicInspector
    from rubric import HypersonicRubric
    from blind_critic import HypersonicBlindCritic
    from elevation_engine import HypersonicElevationEngine

# Import global ActiveDecisionJournal from studio engine
try:
    from src.studio.active_memory import ActiveDecisionJournal
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.studio.active_memory import ActiveDecisionJournal


class ZephyrSterlingMaster:
    """Dr. Zephyr 'The Hypersonic' Sterling: The living hypersonic aerothermodynamics & scramjet sovereign.
    Guarantees Mach 5–25 flight envelope compliance, scramjet isolator shock margin >= 1.25,
    Sutton-Graves aerothermal heat flux modeling, real-gas non-equilibrium dissociation,
    and sub-5ms active unstart mitigation.
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
        self.inspector = HypersonicInspector()
        self.rubric = HypersonicRubric()
        self.critic = HypersonicBlindCritic()
        self.elevation_engine = HypersonicElevationEngine()
        self.journal = ActiveDecisionJournal()

    def run_autonomous_cycle(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """Executes the closed-loop autonomous hypersonic stability audit & elevation lifecycle.
        1. Inspect -> 2. Rubric -> 3. Critic -> 4. Elevate (if < 85) -> 5. Certify & Journal
        """
        data = input_data
        if data is None and self.target_path:
            if os.path.exists(self.target_path):
                with open(self.target_path, "r", encoding="utf-8") as f:
                    data = f.read()
            else:
                raise FileNotFoundError(f"Target hypersonic file not found: {self.target_path}")

        if data is None:
            data = HypersonicReferenceLibrary.get_canonical_core()

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
                sys.stderr.write(f"Note: Could not overwrite target hypersonic file: {_write_err}\n")

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
                target_file=self.target_path if self.target_path else "hypersonic_autonomy_executive.py",
                defects_before=[f"Fatal defects: {fatal_defects}"],
                actions_taken=["zephyr_sterling_hypersonic_scramjet_elevation"],
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
            "⚡ DR. ZEPHYR STERLING — EXECUTIVE HYPERSONIC AEROTHERMODYNAMICS BRIEFING",
            "=" * 78,
            f"Certification Status : {'CERTIFIED' if is_certified else 'REJECTED'}",
            f"Final Safety Score   : {critique['score']:.1f}/100 [{critique['grade']}]",
            f"Fatal Aerothermal Def: {critique['fatal_defects_count']}",
            f"Hypersonic Warnings  : {critique['warnings_count']}",
            "-" * 78,
            "Hypersonic Flight Envelopes & Aerothermodynamic Invariants:",
            "  1. Hypersonic Regime Compliance  : Mach 5.0 to 25.0 atmospheric boundary",
            "  2. Scramjet Isolator Margin      : L_isolator / L_shock >= 1.25 unstart guardrail",
            "  3. Sutton-Graves Aerothermal Heat: q_stag = k_sg * sqrt(rho / R_n) * V^3",
            "  4. Real-Gas Shock Dissociation   : High-temperature enthalpy partitioning T >= 2000K",
            "  5. Thermal Protection System SF  : SF_TPS >= 1.50 with T_surface <= 2500K (UHTC)",
            "  6. Active Unstart Mitigation     : Sub-5.0ms fuel modulation and boundary-layer bleed",
            "=" * 78,
        ]
        return "\n".join(lines)


# Convenient Alias
HypersonicMaster = ZephyrSterlingMaster


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dr. Zephyr Sterling Hypersonic Aerothermodynamics & Scramjet Master"
    )
    parser.add_argument("file", nargs="?", default=None, help="Path to Python hypersonic file to audit")
    parser.add_argument("--elevate", action="store_true", help="Autonomously elevate flawed hypersonic code")
    parser.add_argument("--threshold", type=int, default=85, help="Passing safety score threshold")
    args = parser.parse_args()

    master = ZephyrSterlingMaster(target_path=args.file, passing_threshold=args.threshold)
    result = master.run_autonomous_cycle()

    print(result["executive_briefing"])
    sys.exit(0 if result["is_certified"] else 1)


if __name__ == "__main__":
    main()
