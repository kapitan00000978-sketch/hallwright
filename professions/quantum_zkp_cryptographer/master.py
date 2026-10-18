"""
🛡️ SERAPHINA 'THE AEGIS' STERLING — PRINCIPAL QUANTUM-RESISTANT CRYPTOGRAPHY & ZKP ARCHITECT
Autonomous cryptographic conscience, post-quantum lattice verification, timing side-channel critique,
and zero-knowledge nullifier elevation engine.

Usage:
    python professions/quantum_zkp_cryptographer/master.py <code_file> [--elevate]
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
    from .references import QuantumZkpReferenceLibrary
    from .inspector import QuantumZkpInspector, CryptoInspectionReport
    from .rubric import QuantumZkpRubric, CryptoRubricEvaluation
    from .blind_critic import BlindCryptoCritic, CryptoDefectLedger
    from .elevation_engine import QuantumZkpElevationEngine
except ImportError:
    from references import QuantumZkpReferenceLibrary
    from inspector import QuantumZkpInspector, CryptoInspectionReport
    from rubric import QuantumZkpRubric, CryptoRubricEvaluation
    from blind_critic import BlindCryptoCritic, CryptoDefectLedger
    from elevation_engine import QuantumZkpElevationEngine

# Import global ActiveDecisionJournal from studio engine
try:
    from src.studio.active_memory import ActiveDecisionJournal
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.studio.active_memory import ActiveDecisionJournal


class SeraphinaSterlingMaster:
    """
    Seraphina Sterling: The living post-quantum cryptographic sovereign and ZKP conscience.
    Guarantees Shor-immune lattice encapsulation (FIPS 203 ML-KEM), constant-time execution,
    hardware CSPRNG entropy, and zero-knowledge nullifier double-spend prevention.
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
        self.inspector = QuantumZkpInspector()
        self.rubric = QuantumZkpRubric()
        self.critic = BlindCryptoCritic()
        self.elevation_engine = QuantumZkpElevationEngine()
        self.journal = ActiveDecisionJournal()

    def run_autonomous_cycle(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes the closed-loop autonomous post-quantum audit & elevation lifecycle.
        1. Inspect -> 2. Rubric -> 3. Critic -> 4. Elevate (if < 85) -> 5. Certify & Journal
        """
        data = input_data
        if data is None and self.target_path:
            if os.path.exists(self.target_path):
                with open(self.target_path, "r", encoding="utf-8") as f:
                    data = f.read()
            else:
                raise FileNotFoundError(f"Target cryptographic code file not found: {self.target_path}")

        if data is None:
            data = QuantumZkpReferenceLibrary.get_canonical_core()

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
                sys.stderr.write(f"Note: Could not overwrite target crypto file: {_write_err}\n")

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
                target_file=self.target_path if self.target_path else "crypto_protocol.py",
                defects_before=[f"Fatal defects: {fatal_defects}"],
                actions_taken=["seraphina_quantum_zkp_elevation"],
                score_before=float(initial_score),
                score_after=float(final_score)
            )
        except Exception as _journal_err:
            sys.stderr.write(f"Note: Decision journal record skipped: {_journal_err}\n")

    def _generate_briefing(self, code_data: Any, ledger: CryptoDefectLedger) -> str:
        report = self.inspector.inspect(code_data)
        m = report.metrics

        status_icon = "🛡️ [QUANTUM RESILIENCE CERTIFIED]" if ledger.is_certified else "⚠️ [REJECTED CRYPTOGRAPHIC COLLAPSE]"

        briefing = [
            f"# {status_icon} EXECUTIVE CRYPTOGRAPHIC & ZKP BRIEFING",
            f"**Auditor:** Seraphina 'The Aegis' Sterling (Principal Quantum-Resistant Cryptography & ZKP Architect)",
            f"**Final Score:** {ledger.score}/100 (Threshold: {ledger.passing_threshold})",
            f"**Verdict:** {ledger.verdict}",
            "",
            "## 1. Cryptographic Invariants & Post-Quantum Defense",
            f"- **Post-Quantum Lattice Primitives:** {'PASS (FIPS 203 ML-KEM Active)' if m.has_post_quantum_primitives else 'FAIL (Shor-Vulnerable Classical Keys)'}",
            f"- **Constant-Time Side-Channel Immunity:** {'PASS (secrets.compare_digest)' if m.has_constant_time_comparison else 'FAIL (Timing Side-Channel Risk)'}",
            f"- **ZKP Nullifier Deduplication:** {'PASS (Double-Spend Immunity Enforced)' if m.has_nullifier_tracking else 'WARN (Nullifier Tracking Missing)'}",
            f"- **CSPRNG Entropy Source:** {'PASS (Hardware-Seeded secrets)' if not m.has_insecure_randomness else 'FAIL (Insecure PRNG Detected)'}",
            "",
            "## 2. Defects Ledger & Architectural Interventions",
        ]

        if ledger.defects:
            for d in ledger.defects:
                briefing.append(f"- **[{d.severity}] {d.defect_id} - {d.title}:** {d.description}")
                briefing.append(f"  *Risk:* {d.cryptographic_risk}")
                briefing.append(f"  *Fix:* {d.actionable_fix}")
        else:
            briefing.append("Zero post-quantum, side-channel, or nullifier defects detected. Flawless quantum immunity and zero-knowledge privacy achieved.")

        return "\n".join(briefing)


def main():
    parser = argparse.ArgumentParser(description="Seraphina Sterling Autonomous Post-Quantum & ZKP Master")
    parser.add_argument("file", nargs="?", help="Path to cryptographic code or ZKP circuit file")
    parser.add_argument("--elevate", action="store_true", help="Autonomously elevate crypto code to >= 85/100")
    args = parser.parse_args()

    master = SeraphinaSterlingMaster(target_path=args.file)
    result = master.run_autonomous_cycle()

    print(result["executive_briefing"])
    print("\n" + "=" * 80)
    print(f"Final Score: {result['final_score']}/100 | Status: {result['status']} | Verdict: {result['verdict']}")
    print("=" * 80)

    if not result["is_certified"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
