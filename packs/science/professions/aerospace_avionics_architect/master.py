"""
🛰️ COMMANDER CASSIOPEIA 'THE ORBITAL' STERLING — PRINCIPAL AEROSPACE AVIONICS ARCHITECT
Autonomous mission-critical flight software conscience, TMR majority voting inspection,
blind avionics critique, and radiation-resilient safe-mode elevation engine.

Usage:
    python professions/aerospace_avionics_architect/master.py <code_file> [--elevate]
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception as _enc_err:
        sys.stderr.write(f"Note: UTF-8 stdout reconfiguration skipped: {_enc_err}\n")

try:
    from .references import AvionicsReferenceLibrary
    from .inspector import AvionicsSystemInspector, AvionicsInspectionReport
    from .rubric import AvionicsRubric, AvionicsEvaluation
    from .blind_critic import BlindAvionicsCritic, AvionicsDefectLedger
    from .elevation_engine import AvionicsElevationEngine
except ImportError:
    from references import AvionicsReferenceLibrary
    from inspector import AvionicsSystemInspector, AvionicsInspectionReport
    from rubric import AvionicsRubric, AvionicsEvaluation
    from blind_critic import BlindAvionicsCritic, AvionicsDefectLedger
    from elevation_engine import AvionicsElevationEngine

# Import global ActiveDecisionJournal from studio engine
try:
    from src.studio.active_memory import ActiveDecisionJournal
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.studio.active_memory import ActiveDecisionJournal


class CassiopeiaSterlingMaster:
    """
    Commander Cassiopeia Sterling: The living aerospace avionics sovereign and DO-178C flight conscience.
    Guarantees Triple Modular Redundancy (TMR) majority voting, autonomous safe-mode fallback,
    radiation SEU memory scrubbing, and deterministic ARINC 653 frame execution.
    """

    def __init__(
        self,
        target_path: Optional[str] = None,
        passing_threshold: int = 85,
        max_cycles: int = 3
    ):
        self.target_path = os.path.abspath(target_path) if target_path else None
        self.passing_threshold = passing_threshold
        self.max_cycles = max_cycles
        self.inspector = AvionicsSystemInspector()
        self.rubric = AvionicsRubric()
        self.critic = BlindAvionicsCritic()
        self.elevation_engine = AvionicsElevationEngine()
        self.journal = ActiveDecisionJournal()

    def run_autonomous_cycle(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes the closed-loop autonomous aerospace flight software audit & elevation lifecycle.
        1. Inspect -> 2. Rubric -> 3. Critic -> 4. Elevate (if < 85) -> 5. Certify & Journal
        """
        data = input_data
        if data is None and self.target_path:
            if os.path.exists(self.target_path):
                with open(self.target_path, "r", encoding="utf-8") as f:
                    data = f.read()
            else:
                raise FileNotFoundError(f"Target flight software file not found: {self.target_path}")

        if data is None:
            data = AvionicsReferenceLibrary.get_canonical_core()

        current_data = data
        initial_ledger = self.critic.review(current_data)
        cycles_performed = 0

        # Elevation cycle if below passing threshold
        if not initial_ledger.is_certified:
            elevation_result = self.elevation_engine.elevate(current_data, max_iterations=self.max_cycles)
            current_data = elevation_result["elevated_code"]
            cycles_performed = len(elevation_result.get("remediations_applied", []))

        # Final audit
        final_report = self.inspector.inspect(current_data)
        final_rubric = self.rubric.evaluate(final_report)
        ledger = self.critic.review(current_data)

        # Record decision in persistent Hallwright journal
        self._record_journal_entry(
            initial_score=initial_ledger.score,
            final_score=ledger.score,
            is_certified=ledger.is_certified,
            fatal_defects=ledger.fatal_defects_count,
            verdict=ledger.verdict
        )

        briefing = self._generate_briefing(current_data, ledger)

        # Overwrite file if target path was supplied and code was elevated
        if self.target_path and cycles_performed > 0:
            try:
                with open(self.target_path, "w", encoding="utf-8") as f:
                    f.write(current_data)
            except Exception as _write_err:
                sys.stderr.write(f"Note: Could not overwrite target flight software file: {_write_err}\n")

        return {
            "status": "CERTIFIED" if ledger.is_certified else "REJECTED",
            "initial_score": initial_ledger.score,
            "final_score": ledger.score,
            "is_certified": ledger.is_certified,
            "cycles_performed": cycles_performed,
            "verdict": ledger.verdict,
            "fatal_defects_count": ledger.fatal_defects_count,
            "defects": ledger.defects,
            "elevated_code": current_data,
            "executive_briefing": briefing,
            "summary": ledger.summary
        }

    def _record_journal_entry(
        self,
        initial_score: int,
        final_score: int,
        is_certified: bool,
        fatal_defects: int,
        verdict: str
    ) -> None:
        try:
            self.journal.record_decision(
                iteration=1,
                target_file=self.target_path if self.target_path else "flight_controller.py",
                defects_before=[f"Fatal defects: {fatal_defects}"],
                actions_taken=["cassiopeia_avionics_flight_elevation"],
                score_before=float(initial_score),
                score_after=float(final_score)
            )
        except Exception as _journal_err:
            sys.stderr.write(f"Note: Decision journal record skipped: {_journal_err}\n")

    def _generate_briefing(self, code_data: Any, ledger: AvionicsDefectLedger) -> str:
        report = self.inspector.inspect(code_data)
        m = report.metrics

        status_icon = "🛰️ [ORBITAL FLIGHT CERTIFIED]" if ledger.is_certified else "⚠️ [REJECTED MISSION-CRITICAL HAZARD]"

        briefing = [
            f"# {status_icon} EXECUTIVE AEROSPACE AVIONICS BRIEFING",
            f"**Auditor:** Commander Cassiopeia 'The Orbital' Sterling (Principal Aerospace Avionics Architect)",
            f"**Final Score:** {ledger.score}/100 (Threshold: {self.passing_threshold})",
            f"**Verdict:** {ledger.verdict}",
            "",
            "## 1. Mission-Critical Flight Software Invariants",
            f"- **Triple Modular Redundancy (TMR):** {'PASS (2-out-of-3 Byzantine Quorum)' if m.has_tmr_majority_voting else 'FAIL (Single Point of Failure)'}",
            f"- **Autonomous Safe-Mode Contingency:** {'PASS (Sun-Pointing Safe-Hold Active)' if m.has_autonomous_safe_mode else 'FAIL (Missing Safe-Mode Fallback)'}",
            f"- **Radiation SEU Memory Scrubbing:** {'PASS (Periodic Background EDAC Active)' if m.has_radiation_memory_scrubbing else 'WARN (Unscrubbed Memory Bit-Flips)'}",
            f"- **ARINC 653 Frame Timing:** {'PASS (Monotonic Frame Deadlines Met)' if m.has_deterministic_time_framing else 'WARN (Unchecked Frame Jitter)'}",
            f"- **DO-178C Memory Discipline:** {'PASS (Zero Dynamic Heap Allocations)' if not m.has_dynamic_heap_allocation else 'FAIL (Dynamic Heap Allocation)'}",
            "",
            "## 2. Defects Ledger & Flight Remediation",
        ]

        if ledger.defects:
            for d in ledger.defects:
                briefing.append(f"- **[{d.severity}] {d.id}:** {d.description}")
                briefing.append(f"  *Fix:* {d.actionable_fix}")
        else:
            briefing.append("✅ Zero flight hazards or single points of failure detected. Flight software verified ready for flight computer flashing.")

        return "\n".join(briefing)


def main():
    parser = argparse.ArgumentParser(description="Commander Cassiopeia Sterling Autonomous Aerospace Avionics Master")
    parser.add_argument("target", nargs="?", help="Path to flight control or avionics software file")
    parser.add_argument("--elevate", action="store_true", help="Auto-elevate flawed flight code to 100/100 score")
    args = parser.parse_args()

    master = CassiopeiaSterlingMaster(target_path=args.target)
    result = master.run_autonomous_cycle()

    print(result["executive_briefing"])
    sys.exit(0 if result["is_certified"] else 1)


if __name__ == "__main__":
    main()
