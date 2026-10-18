"""
Hallwright Chaos Fault Injector
Deterministic and probabilistic fault injection module for testing resilience,
circuit breakers, backpressure, and failover mechanics.
"""

from typing import Callable, Any, Optional, Dict
import random
import time
import functools
import contextlib


class ChaosFault(Exception):
    """Base exception raised when artificial chaos faults are triggered."""
    pass


class LatencyChaosFault(ChaosFault):
    pass


class NetworkPartitionFault(ChaosFault):
    pass


class ResourceExhaustionFault(ChaosFault):
    pass


class ChaosInjector:
    """
    Thread-safe chaos monkey engine for simulating production stress scenarios.
    """

    def __init__(self, enabled: bool = True, seed: Optional[int] = None) -> None:
        self.enabled = enabled
        self._rnd = random.Random(seed)
        self._fault_counts: Dict[str, int] = {}

    def maybe_inject_fault(
        self,
        probability: float = 0.1,
        fault_type: type[ChaosFault] = ChaosFault,
        message: str = "Artificial chaos fault injected by Hallwright",
    ) -> None:
        if not self.enabled:
            return

        if self._rnd.random() < probability:
            fault_name = fault_type.__name__
            self._fault_counts[fault_name] = self._fault_counts.get(fault_name, 0) + 1
            raise fault_type(message)

    def maybe_inject_latency(
        self,
        probability: float = 0.1,
        min_delay_ms: float = 50.0,
        max_delay_ms: float = 200.0,
    ) -> float:
        if not self.enabled:
            return 0.0

        if self._rnd.random() < probability:
            delay = self._rnd.uniform(min_delay_ms, max_delay_ms) / 1000.0
            time.sleep(delay)
            self._fault_counts["LatencyDelay"] = self._fault_counts.get("LatencyDelay", 0) + 1
            return delay * 1000.0
        return 0.0

    def wrap(
        self,
        probability: float = 0.1,
        fault_type: type[ChaosFault] = ChaosFault,
        latency_prob: float = 0.0,
        min_delay_ms: float = 50.0,
        max_delay_ms: float = 200.0,
    ) -> Callable:
        """Decorator that wraps a function with chaos injection."""
        def decorator(fn: Callable) -> Callable:
            @functools.wraps(fn)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                if self.enabled:
                    if latency_prob > 0.0:
                        self.maybe_inject_latency(latency_prob, min_delay_ms, max_delay_ms)
                    self.maybe_inject_fault(probability, fault_type)
                return fn(*args, **kwargs)
            return wrapper
        return decorator

    @contextlib.contextmanager
    def fault_scope(self, fault_type: type[ChaosFault] = ChaosFault, message: str = "Scoped fault"):
        if self.enabled:
            self._fault_counts[fault_type.__name__] = self._fault_counts.get(fault_type.__name__, 0) + 1
            raise fault_type(message)
        yield

    def get_stats(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "total_faults_triggered": sum(self._fault_counts.values()),
            "breakdown": dict(self._fault_counts),
        }
