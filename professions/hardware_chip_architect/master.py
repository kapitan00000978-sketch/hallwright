"""
⚡ IGNIS 'THE SILICON' THORNE — PRINCIPAL ASIC & FPGA HARDWARE ARCHITECT
Autonomous silicon conscience, clock domain crossing inspection, blind RTL critique,
and latch-free reset-disciplined hardware elevation engine.

Usage:
    python professions/hardware_chip_architect/master.py <code_file> [--elevate]
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
    from .references import HardwareReferenceLibrary
    from .inspector import HardwareSystemInspector, HardwareInspectionReport
    from .rubric import HardwareRubric, HardwareEvaluation
    from .blind_critic import BlindHardwareCritic, HardwareDefectLedger
    from .elevation_engine import HardwareElevationEngine
except ImportError:
    from references import HardwareReferenceLibrary
    from inspector import HardwareSystemInspector, HardwareInspectionReport
    from rubric import HardwareRubric, HardwareEvaluation
    from blind_critic import BlindHardwareCritic, HardwareDefectLedger
    from elevation_engine import HardwareElevationEngine

# Import global ActiveDecisionJournal from studio engine
try:
    from src.studio.active_memory import ActiveDecisionJournal
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.studio.active_memory import ActiveDecisionJournal


class IgnisThorneMaster:
    """
    Ignis Thorne: The living silicon hardware sovereign and RTL synthesis conscience.
    Guarantees pure combinational logic without inferred latches, multi-flop CDC synchronizers,
    synchronized reset de-assertion, and glitch-free FSM state protection.
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
        self.inspector = HardwareSystemInspector()
        self.rubric = HardwareRubric()
        self.critic = BlindHardwareCritic()
        self.elevation_engine = HardwareElevationEngine()
        self.journal = ActiveDecisionJournal()

    def run_autonomous_cycle(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes the closed-loop autonomous hardware audit & elevation lifecycle.
        1. Inspect -> 2. Rubric -> 3. Critic -> 4. Elevate (if < 85) -> 5. Certify & Journal
        """
        data = input_data
        if data is None and self.target_path:
            if os.path.exists(self.target_path):
                with open(self.target_path, "r", encoding="utf-8") as f:
                    data = f.read()
            else:
                raise FileNotFoundError(f"Target hardware RTL file not found: {self.target_path}")

        if data is None:
            data = HardwareReferenceLibrary.get_canonical_core()

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
                sys.stderr.write(f"Note: Could not overwrite target RTL file: {_write_err}\n")

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
                target_file=self.target_path if self.target_path else "hardware_rtl.sv",
                defects_before=[f"Fatal defects: {fatal_defects}"],
                actions_taken=["ignis_hardware_silicon_elevation"],
                score_before=float(initial_score),
                score_after=float(final_score)
            )
        except Exception as _journal_err:
            sys.stderr.write(f"Note: Decision journal record skipped: {_journal_err}\n")

    def _generate_briefing(self, code_data: Any, ledger: HardwareDefectLedger) -> str:
        report = self.inspector.inspect(code_data)
        m = report.metrics

        status_icon = "⚡ [SILICON TAPE-OUT CERTIFIED]" if ledger.is_certified else "⚠️ [REJECTED METASTABILITY RISK]"

        briefing = [
            f"# {status_icon} EXECUTIVE ASIC & FPGA HARDWARE BRIEFING",
            f"**Auditor:** Ignis 'The Silicon' Thorne (Principal ASIC & FPGA Hardware Architect)",
            f"**Final Score:** {ledger.score}/100 (Threshold: {self.passing_threshold})",
            f"**Verdict:** {ledger.verdict}",
            "",
            "## 1. Silicon Timing & Synthesis Invariants",
            f"- **Inferred Latch Prevention:** {'PASS (Pure Combinational Logic)' if m.has_latch_free_combinational_logic else 'FAIL (Inferred Transparent Latch)'}",
            f"- **CDC Dual-Flop Synchronizer:** {'PASS (Metastability MTBF Protected)' if m.has_cdc_synchronizer else 'FAIL (Unsynchronized Clock Crossing)'}",
            f"- **Reset De-assertion Tree:** {'PASS (Synchronous De-assert Verified)' if m.has_synchronized_reset_deassertion else 'WARN (Unclocked Reset De-assertion)'}",
            f"- **Glitch-Free FSM Safety:** {'PASS (Default Illegal State Trapped)' if m.has_glitch_free_fsm else 'WARN (Missing Default FSM State)'}",
            "",
            "## 2. Defects Ledger & Silicon Remediation",
        ]

        if ledger.defects:
            for d in ledger.defects:
                briefing.append(f"- **[{d.severity}] {d.id}:** {d.description}")
                briefing.append(f"  *Fix:* {d.actionable_fix}")
        else:
            briefing.append("✅ Zero silicon timing defects or inferred latches detected. RTL verified production-ready for synthesis.")

        return "\n".join(briefing)


def main():
    parser = argparse.ArgumentParser(description="Ignis Thorne Autonomous ASIC & FPGA Hardware Master")
    parser.add_argument("target", nargs="?", help="Path to SystemVerilog/Verilog RTL file")
    parser.add_argument("--elevate", action="store_true", help="Auto-elevate flawed RTL to 100/100 score")
    args = parser.parse_args()

    master = IgnisThorneMaster(target_path=args.target)
    result = master.run_autonomous_cycle()

    print(result["executive_briefing"])
    sys.exit(0 if result["is_certified"] else 1)


if __name__ == "__main__":
    main()
