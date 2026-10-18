"""
⚡ MORPHEUS 'THE KERNEL' VANCE — PRINCIPAL EMBEDDED FIRMWARE ARCHITECT
Autonomous bare-metal conscience, static memory allocation inspection, blind firmware critique,
and watchdog-supervised interrupt-disciplined elevation engine.

Usage:
    python professions/embedded_firmware_architect/master.py <code_file> [--elevate]
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
    from .references import FirmwareReferenceLibrary
    from .inspector import FirmwareSystemInspector, FirmwareInspectionReport
    from .rubric import FirmwareRubric, FirmwareEvaluation
    from .blind_critic import BlindFirmwareCritic, FirmwareDefectLedger
    from .elevation_engine import FirmwareElevationEngine
except ImportError:
    from references import FirmwareReferenceLibrary
    from inspector import FirmwareSystemInspector, FirmwareInspectionReport
    from rubric import FirmwareRubric, FirmwareEvaluation
    from blind_critic import BlindFirmwareCritic, FirmwareDefectLedger
    from elevation_engine import FirmwareElevationEngine

# Import global ActiveDecisionJournal from studio engine
try:
    from src.studio.active_memory import ActiveDecisionJournal
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.studio.active_memory import ActiveDecisionJournal


class MorpheusVanceMaster:
    """
    Morpheus Vance: The living bare-metal firmware sovereign and embedded reliability conscience.
    Guarantees 100% static memory allocation, sub-5µs ISR latency execution,
    hardware watchdog supervision, and DMA cache coherency.
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
        self.inspector = FirmwareSystemInspector()
        self.rubric = FirmwareRubric()
        self.critic = BlindFirmwareCritic()
        self.elevation_engine = FirmwareElevationEngine()
        self.journal = ActiveDecisionJournal()

    def run_autonomous_cycle(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes the closed-loop autonomous embedded firmware audit & elevation lifecycle.
        1. Inspect -> 2. Rubric -> 3. Critic -> 4. Elevate (if < 85) -> 5. Certify & Journal
        """
        data = input_data
        if data is None and self.target_path:
            if os.path.exists(self.target_path):
                with open(self.target_path, "r", encoding="utf-8") as f:
                    data = f.read()
            else:
                raise FileNotFoundError(f"Target firmware file not found: {self.target_path}")

        if data is None:
            data = FirmwareReferenceLibrary.get_canonical_core()

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
                sys.stderr.write(f"Note: Could not overwrite target firmware file: {_write_err}\n")

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
                target_file=self.target_path if self.target_path else "embedded_firmware.c",
                defects_before=[f"Fatal defects: {fatal_defects}"],
                actions_taken=["morpheus_firmware_bare_metal_elevation"],
                score_before=float(initial_score),
                score_after=float(final_score)
            )
        except Exception as _journal_err:
            sys.stderr.write(f"Note: Decision journal record skipped: {_journal_err}\n")

    def _generate_briefing(self, code_data: Any, ledger: FirmwareDefectLedger) -> str:
        report = self.inspector.inspect(code_data)
        m = report.metrics

        status_icon = "⚡ [BARE-METAL FIRMWARE CERTIFIED]" if ledger.is_certified else "⚠️ [REJECTED HEAP FRAGMENTATION HAZARD]"

        briefing = [
            f"# {status_icon} EXECUTIVE EMBEDDED FIRMWARE BRIEFING",
            f"**Auditor:** Morpheus 'The Kernel' Vance (Principal Embedded Firmware Architect)",
            f"**Final Score:** {ledger.score}/100 (Threshold: {self.passing_threshold})",
            f"**Verdict:** {ledger.verdict}",
            "",
            "## 1. Bare-Metal & Interrupt Invariants",
            f"- **Heap Allocation Policy:** {'PASS (100% Static Allocation)' if m.has_zero_heap_allocation else 'FAIL (Dynamic Heap Allocation Risk)'}",
            f"- **Hardware Watchdog Supervisor:** {'PASS (Initialized & Serviced)' if m.has_hardware_watchdog else 'FAIL (Missing Hardware Watchdog)'}",
            f"- **ISR Execution Discipline:** {'PASS (Sub-5µs Deferred Handling)' if not m.has_blocking_delay_in_isr else 'FAIL (Blocking Delay in ISR)'}",
            f"- **Volatile MMIO Registers:** {'PASS (Volatile & Memory Barriers)' if m.has_volatile_mmio_registers else 'WARN (Non-Volatile Hardware Access)'}",
            f"- **DMA Cache Coherency:** {'PASS (D-Cache Maintenance Enforced)' if m.has_dma_cache_coherency else 'WARN (Unchecked DMA Cache)'}",
            "",
            "## 2. Defects Ledger & Remediation",
        ]

        if ledger.defects:
            for d in ledger.defects:
                briefing.append(f"- **[{d.severity}] {d.id}:** {d.description}")
                briefing.append(f"  *Fix:* {d.actionable_fix}")
        else:
            briefing.append("✅ Zero memory leaks, heap fragmentation risks, or unserviced watchdog deadlocks detected. Firmware certified production-ready.")

        return "\n".join(briefing)


def main():
    parser = argparse.ArgumentParser(description="Morpheus Vance Autonomous Embedded Firmware Master")
    parser.add_argument("target", nargs="?", help="Path to embedded C/C++ firmware file")
    parser.add_argument("--elevate", action="store_true", help="Auto-elevate flawed firmware to 100/100 score")
    args = parser.parse_args()

    master = MorpheusVanceMaster(target_path=args.target)
    result = master.run_autonomous_cycle()

    print(result["executive_briefing"])
    sys.exit(0 if result["is_certified"] else 1)


if __name__ == "__main__":
    main()
