"""🧬 DR. SERAPHIEL 'THE SYNBIO' STERLING — SYNTHETIC BIOLOGY ARCHITECT
Autonomous genetic circuit audit, Hill cooperativity transfer function verification,
cellular metabolic burden defense, and multi-layer biocontainment elevation engine.

Usage:
    python professions/synthetic_biology_architect/master.py <code_file> [--elevate]
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
    from .references import SynBioReferenceLibrary
    from .inspector import SynBioInspector
    from .rubric import SynBioRubric
    from .blind_critic import SynBioBlindCritic
    from .elevation_engine import SynBioElevationEngine
except ImportError:
    from references import SynBioReferenceLibrary
    from inspector import SynBioInspector
    from rubric import SynBioRubric
    from blind_critic import SynBioBlindCritic
    from elevation_engine import SynBioElevationEngine

# Import global ActiveDecisionJournal from studio engine
try:
    from src.studio.active_memory import ActiveDecisionJournal
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.studio.active_memory import ActiveDecisionJournal


class SeraphielSterlingMaster:
    """Dr. Seraphiel 'The SynBio' Sterling: The living synthetic biology & metabolic circuit sovereign.
    Guarantees non-linear Hill cooperativity (n >= 2.0), metabolic burden <= 30%,
    transcriptional crosstalk <= 5%, and multi-layer biocontainment escape <= 1e-8.
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
        self.inspector = SynBioInspector()
        self.rubric = SynBioRubric()
        self.critic = SynBioBlindCritic()
        self.elevation_engine = SynBioElevationEngine()
        self.journal = ActiveDecisionJournal()

    def run_autonomous_cycle(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """Executes the closed-loop autonomous synthetic biology audit & elevation lifecycle.
        1. Inspect -> 2. Rubric -> 3. Critic -> 4. Elevate (if < 85) -> 5. Certify & Journal
        """
        data = input_data
        if data is None and self.target_path:
            if os.path.exists(self.target_path):
                with open(self.target_path, "r", encoding="utf-8") as f:
                    data = f.read()
            else:
                raise FileNotFoundError(f"Target synthetic biology file not found: {self.target_path}")

        if data is None:
            data = SynBioReferenceLibrary.get_canonical_core()

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
                sys.stderr.write(f"Note: Could not overwrite target synbio file: {_write_err}\n")

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
                target_file=self.target_path if self.target_path else "genetic_circuit_executive.py",
                defects_before=[f"Fatal defects: {fatal_defects}"],
                actions_taken=["seraphiel_sterling_synbio_circuit_elevation"],
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
            "🧬 DR. SERAPHIEL STERLING — EXECUTIVE SYNTHETIC BIOLOGY BRIEFING",
            "=" * 78,
            f"Certification Status : {'CERTIFIED' if is_certified else 'REJECTED'}",
            f"Final Safety Score   : {critique['score']:.1f}/100 [{critique['grade']}]",
            f"Fatal Circuit Defects: {critique['fatal_defects_count']}",
            f"Biosafety Warnings   : {critique['warnings_count']}",
            "-" * 78,
            "Synthetic Biology Genetic Circuit & Biocontainment Invariants:",
            "  1. Hill Cooperativity Index     : n >= 2.0 (discrete bistable switching)",
            "  2. Dynamic Range (ON/OFF Ratio) : R >= 20.0x basal leakage containment",
            "  3. Cellular Metabolic Burden    : Burden <= 30.0% cellular translation budget",
            "  4. Orthogonal Transcriptome     : Crosstalk <= 5.0% host regulatory isolation",
            "  5. Biocontainment Escape Bound  : P_escape <= 1.0e-8 (NIH recombinant DNA standard)",
            "  6. Redundant Suicide Kill Switch: Sub-60.0min multi-layer Cas3/toxin lysis",
            "=" * 78,
        ]
        return "\n".join(lines)


# Convenient Alias
SynBioMaster = SeraphielSterlingMaster


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dr. Seraphiel Sterling Synthetic Biology & Genetic Circuit Master"
    )
    parser.add_argument("file", nargs="?", default=None, help="Path to Python synbio file to audit")
    parser.add_argument("--elevate", action="store_true", help="Autonomously elevate flawed synbio code")
    parser.add_argument("--threshold", type=int, default=85, help="Passing safety score threshold")
    args = parser.parse_args()

    master = SeraphielSterlingMaster(target_path=args.file, passing_threshold=args.threshold)
    result = master.run_autonomous_cycle()

    print(result["executive_briefing"])
    sys.exit(0 if result["is_certified"] else 1)


if __name__ == "__main__":
    main()
