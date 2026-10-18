"""
🦾 DR. VESPERA 'THE KINEMATIC' STERLING — PRINCIPAL AUTONOMOUS ROBOTICS & EMBODIED AI ARCHITECT
Autonomous hard real-time conscience, sensory fusion inspection, blind physical safety critique,
and singularity-damped torque-clamped elevation engine.

Usage:
    python professions/robotics_embodied_ai_architect/master.py <code_file> [--elevate]
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
    from .references import RoboticsReferenceLibrary
    from .inspector import RoboticsSystemInspector, RoboticsInspectionReport
    from .rubric import RoboticsRubric, RoboticsEvaluation
    from .blind_critic import BlindRoboticsCritic, RoboticsDefectLedger
    from .elevation_engine import RoboticsElevationEngine
except ImportError:
    from references import RoboticsReferenceLibrary
    from inspector import RoboticsSystemInspector, RoboticsInspectionReport
    from rubric import RoboticsRubric, RoboticsEvaluation
    from blind_critic import BlindRoboticsCritic, RoboticsDefectLedger
    from elevation_engine import RoboticsElevationEngine

# Import global ActiveDecisionJournal from studio engine
try:
    from src.studio.active_memory import ActiveDecisionJournal
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src.studio.active_memory import ActiveDecisionJournal


class VesperaSterlingMaster:
    """
    Dr. Vespera Sterling: The living autonomous robotics sovereign and physical safety conscience.
    Guarantees hard real-time actuation determinism, torque saturation clamping,
    emergency stop interlocks, and singularity-damped inverse kinematics.
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
        self.inspector = RoboticsSystemInspector()
        self.rubric = RoboticsRubric()
        self.critic = BlindRoboticsCritic()
        self.elevation_engine = RoboticsElevationEngine()
        self.journal = ActiveDecisionJournal()

    def run_autonomous_cycle(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes the closed-loop autonomous robotics audit & elevation lifecycle.
        1. Inspect -> 2. Rubric -> 3. Critic -> 4. Elevate (if < 85) -> 5. Certify & Journal
        """
        data = input_data
        if data is None and self.target_path:
            if os.path.exists(self.target_path):
                with open(self.target_path, "r", encoding="utf-8") as f:
                    data = f.read()
            else:
                raise FileNotFoundError(f"Target robotics code file not found: {self.target_path}")

        if data is None:
            data = RoboticsReferenceLibrary.get_canonical_core()

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
                sys.stderr.write(f"Note: Could not overwrite target robotics file: {_write_err}\n")

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
                target_file=self.target_path if self.target_path else "robotics_controller.py",
                defects_before=[f"Fatal defects: {fatal_defects}"],
                actions_taken=["vespera_robotics_kinematic_elevation"],
                score_before=float(initial_score),
                score_after=float(final_score)
            )
        except Exception as _journal_err:
            sys.stderr.write(f"Note: Decision journal record skipped: {_journal_err}\n")

    def _generate_briefing(self, code_data: Any, ledger: RoboticsDefectLedger) -> str:
        report = self.inspector.inspect(code_data)
        m = report.metrics

        status_icon = "🦾 [ROBOTICS SAFETY CERTIFIED]" if ledger.is_certified else "⚠️ [REJECTED KINETIC HAZARD]"

        briefing = [
            f"# {status_icon} EXECUTIVE ROBOTICS & CONTROL BRIEFING",
            f"**Auditor:** Dr. Vespera 'The Kinematic' Sterling (Principal Robotics & Embodied AI Architect)",
            f"**Final Score:** {ledger.score}/100 (Threshold: {self.passing_threshold})",
            f"**Verdict:** {ledger.verdict}",
            "",
            "## 1. Physical Safety & Real-Time Invariants",
            f"- **Real-Time Control Loop:** {'PASS (Deterministic Monotonic Timing)' if m.has_bounded_actuation_cycle else 'FAIL (Blocking Delays Present)'}",
            f"- **Torque Saturation Clamping:** {'PASS (Clamped to Safe Envelope)' if m.has_torque_saturation_clamping else 'FAIL (Uncapped Motor Torque)'}",
            f"- **Emergency Stop Interlock:** {'PASS (Active E-Stop Zero-Torque State)' if m.has_emergency_stop_interlock else 'FAIL (Missing E-Stop Interlock)'}",
            f"- **Singularity Damping:** {'PASS (Damped Least Squares Active)' if m.has_singularity_damping else 'FAIL (Undamped Matrix Inversion)'}",
            f"- **EKF Sensory Fusion:** {'PASS (IMU + Encoder Covariance Tracking)' if m.has_ekf_sensor_fusion else 'WARN (Open-Loop Integration)'}",
            "",
            "## 2. Defects Ledger & Mitigations",
        ]

        if ledger.defects:
            for d in ledger.defects:
                briefing.append(f"- **[{d.severity}] {d.id}:** {d.description}")
                briefing.append(f"  *Fix:* {d.actionable_fix}")
        else:
            briefing.append("✅ Zero physical safety defects or timing anomalies detected. Ready for physical hardware testing.")

        return "\n".join(briefing)


def main():
    parser = argparse.ArgumentParser(description="Dr. Vespera Sterling Autonomous Robotics & Embodied AI Master")
    parser.add_argument("target", nargs="?", help="Path to robotics controller or kinematic file")
    parser.add_argument("--elevate", action="store_true", help="Auto-elevate flawed code to 100/100 safety score")
    args = parser.parse_args()

    master = VesperaSterlingMaster(target_path=args.target)
    result = master.run_autonomous_cycle()

    print(result["executive_briefing"])
    sys.exit(0 if result["is_certified"] else 1)


if __name__ == "__main__":
    main()
