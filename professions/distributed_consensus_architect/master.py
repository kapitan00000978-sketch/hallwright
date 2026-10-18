"""
🌐 SOREN 'THE CONDUCTOR' LINDQVIST — PRINCIPAL DISTRIBUTED CONSENSUS & PROTOCOL ARCHITECT
Autonomous protocol conscience, majority quorum verification, blind fork critique,
and deterministic term-fenced consensus elevation engine.

Usage:
    python professions/distributed_consensus_architect/master.py <code_file> [--elevate]
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
    from .references import ConsensusReferenceLibrary
    from .inspector import ConsensusSystemInspector, ConsensusInspectionReport
    from .rubric import ConsensusProtocolRubric, ConsensusRubricEvaluation
    from .blind_critic import BlindConsensusCritic, ConsensusDefectLedger
    from .elevation_engine import ConsensusElevationEngine
except ImportError:
    from references import ConsensusReferenceLibrary
    from inspector import ConsensusSystemInspector, ConsensusInspectionReport
    from rubric import ConsensusProtocolRubric, ConsensusRubricEvaluation
    from blind_critic import BlindConsensusCritic, ConsensusDefectLedger
    from elevation_engine import ConsensusElevationEngine

# Import global ActiveDecisionJournal from studio engine
try:
    from src.studio.active_memory import ActiveDecisionJournal
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.studio.active_memory import ActiveDecisionJournal


class SorenLindqvistMaster:
    """
    Soren Lindqvist: The living distributed consensus sovereign and protocol conscience.
    Guarantees mathematically proven quorum boundaries ((N/2)+1), monotonic term fencing,
    re-entrancy immunity, and deterministic state transitions.
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
        self.inspector = ConsensusSystemInspector()
        self.rubric = ConsensusProtocolRubric()
        self.critic = BlindConsensusCritic()
        self.elevation_engine = ConsensusElevationEngine()
        self.journal = ActiveDecisionJournal()

    def run_autonomous_cycle(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes the closed-loop autonomous consensus protocol audit & elevation lifecycle.
        1. Inspect -> 2. Rubric -> 3. Critic -> 4. Elevate (if < 85) -> 5. Certify & Journal
        """
        data = input_data
        if data is None and self.target_path:
            if os.path.exists(self.target_path):
                with open(self.target_path, "r", encoding="utf-8") as f:
                    data = f.read()
            else:
                raise FileNotFoundError(f"Target consensus specification file not found: {self.target_path}")

        if data is None:
            data = ConsensusReferenceLibrary.get_canonical_consensus_core()

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
                sys.stderr.write(f"Note: Could not overwrite target consensus file: {_write_err}\n")

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
            "summary": ledger.critic_verdict_summary
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
                target_file=self.target_path if self.target_path else "consensus_state_machine.py",
                defects_before=[f"Fatal defects: {fatal_defects}"],
                actions_taken=["soren_consensus_protocol_elevation"],
                score_before=float(initial_score),
                score_after=float(final_score)
            )
        except Exception as _journal_err:
            sys.stderr.write(f"Note: Decision journal record skipped: {_journal_err}\n")

    def _generate_briefing(self, code_data: Any, ledger: ConsensusDefectLedger) -> str:
        report = self.inspector.inspect(code_data)
        m = report.metrics

        status_icon = "🌐 [DETERMINISTIC CONSENSUS CERTIFIED]" if ledger.is_certified else "⚠️ [REJECTED PARTITION DIVERGENCE]"

        briefing = [
            f"# {status_icon} EXECUTIVE DISTRIBUTED CONSENSUS BRIEFING",
            f"**Auditor:** Soren 'The Conductor' Lindqvist (Principal Distributed Consensus & Protocol Architect)",
            f"**Final Score:** {ledger.score}/100 (Threshold: {ledger.passing_threshold})",
            f"**Verdict:** {ledger.verdict}",
            "",
            "## 1. Protocol Invariants & Quorum Discipline",
            f"- **Majority Quorum ((N/2)+1):** {'PASS (Strict Majority Enforced)' if m.has_quorum_majority_check else 'FAIL (Split-Brain Risk)'}",
            f"- **Monotonic Term Fencing:** {'PASS (Stale Leaders Rejected)' if m.has_term_fencing_validation else 'WARN (Epoch Fencing Missing)'}",
            f"- **Re-Entrancy Defense (CEI):** {'PASS (Atomic Mutex Enforced)' if m.has_reentrancy_protection else 'FAIL (Ledger Drain Vulnerability)'}",
            f"- **State Machine Determinism:** {'PASS (Pure Transition Functions)' if m.has_deterministic_state_transitions else 'FAIL (Wall-Clock / Random Flaw)'}",
            "",
            "## 2. Defects Ledger & Architectural Interventions",
        ]

        if ledger.defects:
            for d in ledger.defects:
                briefing.append(f"- **[{d.severity}] {d.defect_id} - {d.title}:** {d.description}")
                briefing.append(f"  *Risk:* {d.protocol_risk}")
                briefing.append(f"  *Fix:* {d.actionable_fix}")
        else:
            briefing.append("Zero protocol, quorum, or re-entrancy defects detected. Flawless Byzantine resilience and consensus determinism achieved.")

        return "\n".join(briefing)


def main():
    parser = argparse.ArgumentParser(description="Soren Lindqvist Autonomous Distributed Consensus Master")
    parser.add_argument("file", nargs="?", help="Path to state machine or consensus protocol code file")
    parser.add_argument("--elevate", action="store_true", help="Autonomously elevate consensus code to >= 85/100")
    args = parser.parse_args()

    master = SorenLindqvistMaster(target_path=args.file)
    result = master.run_autonomous_cycle()

    print(result["executive_briefing"])
    print("\n" + "=" * 80)
    print(f"Final Score: {result['final_score']}/100 | Status: {result['status']} | Verdict: {result['verdict']}")
    print("=" * 80)

    if not result["is_certified"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
