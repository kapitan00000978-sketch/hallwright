"""
Step 7 — The Studio Orchestrator (Dirijyor)
Controls the entire autonomous feedback loop:
- Who runs when
- Max attempts budget (default: 3 iterations)
- Time budget
- When to stop (Threshold >= 80)
- When to escalate to human
- Interacts with Active Decision Journal
"""

import sys
import os
import time
from typing import Dict, Any, List, Optional

from .reference_collector import ReferenceCollector
from .measurement_layer import MeasurementLayer
from .rubric_engine import RubricEngine
from .blind_critic import BlindCritic
from .remediator_loop import RemediatorAgent
from .active_memory import ActiveDecisionJournal


class StudioOrchestrator:
    """
    The Conductor of the Craftsman Studio.
    Orchestrates Collector -> Measurement -> Rubric -> Blind Critic -> Remediator -> Active Memory loop.
    """

    def __init__(
        self,
        target_file: str,
        profile_name: str = "saas_landing",
        passing_threshold: float = 80.0,
        max_iterations: int = 3,
        timeout_seconds: int = 60
    ):
        self.target_file = os.path.abspath(target_file)
        self.profile_name = profile_name
        self.passing_threshold = passing_threshold
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds

        # Instantiate components
        self.collector = ReferenceCollector(profile_name=profile_name)
        self.rubric = RubricEngine()
        self.critic = BlindCritic(rubric_threshold=passing_threshold)
        self.remediator = RemediatorAgent()
        self.journal = ActiveDecisionJournal()

    def run(self, auto_remediate: bool = True) -> Dict[str, Any]:
        """
        Executes the closed-loop autonomous quality cycle.
        """
        start_time = time.time()
        print("\n" + "=" * 80)
        print("  🎼 HALLWRIGHT STUDIO ORCHESTRATOR — THE CONDUCTOR ACTIVE")
        print(f"     Target: {os.path.basename(self.target_file)} | Profile: {self.profile_name} | Target: >={self.passing_threshold}/100")
        print("=" * 80)

        reference_profile = self.collector.get_benchmark_profile()
        history: List[Dict[str, Any]] = []

        for iteration in range(1, self.max_iterations + 1):
            elapsed = time.time() - start_time
            if elapsed >= self.timeout_seconds:
                print(f"⏱️ [Orchestrator Timeout]: Reached {self.timeout_seconds}s time budget. Ending loop.")
                break

            print(f"\n--- [Cycle {iteration}/{self.max_iterations}] Objective Measurement & Blind Evaluation ---")

            # 1. Measure
            measurement_layer = MeasurementLayer(self.target_file)
            measurements = measurement_layer.measure()

            # 2. Rubric Evaluation
            rubric_eval = self.rubric.evaluate(measurements, reference_profile)

            # 3. Blind Critique (Outcome-only)
            audit_result = self.critic.audit(rubric_eval, measurements)
            score = audit_result["total_score"]

            print(f"📊 Quantitative Score: {score}/100 | Verdict: {audit_result['verdict']}")
            for dim, item in rubric_eval["dimensions"].items():
                print(f"   • {dim:<25}: {item['score']:>4}/10 | Measured: {item['measured']} [{item['status']}]")

            history.append({
                "iteration": iteration,
                "score": score,
                "verdict": audit_result["verdict"],
                "defects": audit_result["defect_ledger"]
            })

            # Check if certified
            if audit_result["passed"]:
                print("\n" + "=" * 80)
                print(f"  🏆 [CERTIFIED WORLD-CLASS]: Passed all rubrics! Score: {score}/100 in cycle {iteration}.")
                print("=" * 80)
                return {
                    "status": "CERTIFIED",
                    "final_score": score,
                    "iterations_used": iteration,
                    "history": history,
                    "target_file": self.target_file
                }

            if not auto_remediate or iteration == self.max_iterations:
                break

            # 4. Remediation Loop
            defects = audit_result["defect_ledger"]
            defect_desc = [d["issue"] for d in defects]
            print(f"\n🔧 [Remediator Dispatched]: {len(defects)} structural defects identified by Blind Critic.")
            for d in defects:
                print(f"   ⚠️  [{d['severity']}] {d['issue']}")

            repaired = self.remediator.apply_remediations(self.target_file, defects)
            print(f"   ✅ Executed {len(repaired)} surgical fixes.")

            # Measure post-remediation score for decision journal
            post_meas = MeasurementLayer(self.target_file).measure()
            post_score = self.rubric.evaluate(post_meas, reference_profile)["total_score"]

            # 5. Record to Active Decision Journal (Learning from scar tissue)
            self.journal.record_decision(
                iteration=iteration,
                target_file=self.target_file,
                defects_before=defect_desc,
                actions_taken=repaired,
                score_before=score,
                score_after=post_score
            )
            print(f"   🧠 Active Decision Journal updated. (Score Delta: {round(post_score - score, 1):+f})")

        # Escalate to human if budget exhausted without certification
        final_score = history[-1]["score"]
        print("\n" + "=" * 80)
        print(f"  ⚠️ [ORCHESTRATOR HANDOFF]: Loop completed after {len(history)} cycles. Final Score: {final_score}/100")
        print("     Reason: Highest autonomous quality threshold not fully certified. Handing off to human master.")
        print("=" * 80)

        return {
            "status": "HANDOFF_REQUIRED",
            "final_score": final_score,
            "iterations_used": len(history),
            "history": history,
            "target_file": self.target_file
        }
