"""Hallwright Enterprise Architecture Library: Circuit Breaker.

Provides resilient fault-tolerance for distributed calls, network requests,
and unreliable subsystems, preventing cascading failures with exponential backoff.
"""

from enum import Enum
from typing import Callable, Any, Optional
import time
from functools import wraps


class CircuitState(Enum):
    """Lifecycle states of the Circuit Breaker."""
    CLOSED = "CLOSED"        # Normal operation: requests pass through
    OPEN = "OPEN"            # Tripped: requests fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing: limited probe requests allowed


class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while the circuit breaker is OPEN."""
    pass


class CircuitBreaker:
    """Thread-safe, fault-tolerant Circuit Breaker pattern.

    Features:
    - Failure threshold detection within sliding windows
    - Automatic state transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED)
    - Fallback handler execution support
    - Configurable reset timeouts and success thresholds in HALF_OPEN
    - Telemetry tracking (total calls, failures, successes, trips)
    """

    def __init__(
        self,
        name: str = "default_circuit",
        failure_threshold: int = 5,
        recovery_timeout_sec: float = 30.0,
        half_open_success_threshold: int = 2,
        fallback: Optional[Callable[..., Any]] = None,
    ):
        self.name = name
        self.failure_threshold = max(1, failure_threshold)
        self.recovery_timeout_sec = max(0.1, recovery_timeout_sec)
        self.half_open_success_threshold = max(1, half_open_success_threshold)
        self.fallback = fallback

        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._last_state_change = time.time()
        self._last_failure_time = 0.0

        # Telemetry
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.trip_count = 0

    @property
    def state(self) -> CircuitState:
        """Return the current circuit state, updating from timeout if necessary."""
        self._evaluate_state()
        return self._state

    def _evaluate_state(self) -> None:
        """Check if OPEN circuit has exceeded recovery timeout to become HALF_OPEN."""
        if self._state == CircuitState.OPEN:
            elapsed = time.time() - self._last_state_change
            if elapsed >= self.recovery_timeout_sec:
                self._transition_to(CircuitState.HALF_OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        """Atomic state transition."""
        self._state = new_state
        self._last_state_change = time.time()
        if new_state == CircuitState.OPEN:
            self.trip_count += 1
            self._consecutive_successes = 0
        elif new_state == CircuitState.CLOSED:
            self._consecutive_failures = 0
            self._consecutive_successes = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._consecutive_successes = 0

    def record_success(self) -> None:
        """Record an operation success."""
        self.total_calls += 1
        self.total_successes += 1
        self._consecutive_failures = 0

        if self._state == CircuitState.HALF_OPEN:
            self._consecutive_successes += 1
            if self._consecutive_successes >= self.half_open_success_threshold:
                self._transition_to(CircuitState.CLOSED)

    def record_failure(self, error: Exception) -> None:
        """Record an operation failure and trip the circuit if threshold exceeded."""
        self.total_calls += 1
        self.total_failures += 1
        self._consecutive_failures += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
        elif self._state == CircuitState.CLOSED:
            if self._consecutive_failures >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)

    def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute a function under the protection of the circuit breaker."""
        self._evaluate_state()

        if self._state == CircuitState.OPEN:
            if self.fallback:
                return self.fallback(*args, **kwargs)
            raise CircuitBreakerOpenException(
                f"Circuit '{self.name}' is OPEN. Fast-failing execution."
            )

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as exc:
            self.record_failure(exc)
            if self.fallback:
                return self.fallback(*args, **kwargs)
            raise

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator interface for wrapping functions with circuit protection."""
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return self.execute(func, *args, **kwargs)
        return wrapper
