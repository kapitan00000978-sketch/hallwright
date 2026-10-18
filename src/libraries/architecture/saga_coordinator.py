"""
Hallwright Distributed Saga Coordinator
Zero-dependency orchestrator for multi-step agent operations with compensation (rollback) chains.
"""

from typing import Callable, Any, Dict, List, Optional
from dataclasses import dataclass, field
import enum
import time
import logging

logger = logging.getLogger("hallwright.architecture.saga")


class SagaStepStatus(enum.Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    COMPENSATION_FAILED = "compensation_failed"


@dataclass
class SagaStep:
    name: str
    action: Callable[[Dict[str, Any]], Any]
    compensation: Optional[Callable[[Dict[str, Any]], Any]] = None
    status: SagaStepStatus = SagaStepStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0


class SagaState(enum.Enum):
    INITIALIZED = "initialized"
    RUNNING = "running"
    SUCCESS = "success"
    ROLLED_BACK = "rolled_back"
    COMPENSATION_FAILED = "compensation_failed"


class SagaCoordinator:
    """
    Transactional Saga Coordinator for orchestrating multi-agent workflows.
    Ensures that if step N fails, steps N-1 down to 0 are compensated in reverse order.
    """

    def __init__(self, name: str = "default_saga") -> None:
        self.name = name
        self.steps: List[SagaStep] = []
        self.state: SagaState = SagaState.INITIALIZED
        self.context: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []

    def add_step(
        self,
        name: str,
        action: Callable[[Dict[str, Any]], Any],
        compensation: Optional[Callable[[Dict[str, Any]], Any]] = None,
    ) -> "SagaCoordinator":
        """Registers a forward action and its optional compensating rollback action."""
        if self.state != SagaState.INITIALIZED:
            raise RuntimeError(f"Cannot add steps when saga is in state {self.state}")
        self.steps.append(SagaStep(name=name, action=action, compensation=compensation))
        return self

    def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Executes the saga sequentially. If any step fails, compensation actions
        are executed in LIFO (reverse) order.
        Returns True if successful, False if compensated or failed.
        """
        self.context = dict(initial_context or {})
        self.state = SagaState.RUNNING
        executed_steps: List[SagaStep] = []

        for step in self.steps:
            step.status = SagaStepStatus.EXECUTING
            start = time.perf_counter()
            try:
                step_result = step.action(self.context)
                step.duration_ms = (time.perf_counter() - start) * 1000
                step.status = SagaStepStatus.COMPLETED
                step.result = step_result
                if isinstance(step_result, dict):
                    self.context.update(step_result)
                executed_steps.append(step)
                self._record_history(step, "action_success")
            except Exception as e:
                step.duration_ms = (time.perf_counter() - start) * 1000
                step.status = SagaStepStatus.FAILED
                step.error = str(e)
                self._record_history(step, f"action_failure: {e}")
                logger.error("Saga step %s failed: %s. Initiating compensation chain.", step.name, e)
                self._compensate(executed_steps)
                return False

        self.state = SagaState.SUCCESS
        return True

    def _compensate(self, completed_steps: List[SagaStep]) -> None:
        """Rolls back all completed steps in reverse order."""
        failed_compensation = False

        for step in reversed(completed_steps):
            if step.compensation:
                step.status = SagaStepStatus.COMPENSATING
                start = time.perf_counter()
                try:
                    step.compensation(self.context)
                    step.status = SagaStepStatus.COMPENSATED
                    self._record_history(step, "compensation_success")
                except Exception as comp_err:
                    step.status = SagaStepStatus.COMPENSATION_FAILED
                    step.error = f"Compensation failed: {comp_err}"
                    failed_compensation = True
                    self._record_history(step, f"compensation_failure: {comp_err}")
                    logger.critical("Fatal: Compensation for %s failed: %s", step.name, comp_err)
            else:
                step.status = SagaStepStatus.COMPENSATED

        self.state = SagaState.COMPENSATION_FAILED if failed_compensation else SagaState.ROLLED_BACK

    def _record_history(self, step: SagaStep, event: str) -> None:
        self.history.append({
            "step": step.name,
            "status": step.status.value,
            "event": event,
            "duration_ms": round(step.duration_ms, 3),
            "timestamp": time.time(),
        })

    def get_summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "step_count": len(self.steps),
            "history": list(self.history),
        }
