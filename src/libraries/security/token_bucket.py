"""Hallwright Enterprise Security Library: Token Bucket Rate Limiter.

Provides a thread-safe, microsecond-accurate token bucket rate limiter
to guard APIs and sensitive functions against brute-force and Denial-of-Service (DoS).
"""

import time
import threading
from typing import Optional


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded and non-blocking acquire is attempted."""
    pass


class TokenBucketRateLimiter:
    """Thread-safe Token Bucket Rate Limiter.

    Features:
    - Fractional token accumulation based on wall-clock drift
    - Burst limit handling up to maximum capacity
    - Blocking with timeout or non-blocking try_acquire modes
    - Remaining token and wait time calculation
    """

    def __init__(self, capacity: float, refill_rate_per_sec: float):
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        if refill_rate_per_sec <= 0:
            raise ValueError("Refill rate must be positive.")

        self.capacity: float = float(capacity)
        self.refill_rate: float = float(refill_rate_per_sec)
        self._tokens: float = float(capacity)
        self._last_refill: float = time.time()
        self._lock: threading.Lock = threading.Lock()

    def _refill(self) -> None:
        """Internal replenishment based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_refill
        if elapsed > 0:
            new_tokens = elapsed * self.refill_rate
            self._tokens = min(self.capacity, self._tokens + new_tokens)
            self._last_refill = now

    def available_tokens(self) -> float:
        """Return the current number of available tokens."""
        with self._lock:
            self._refill()
            return self._tokens

    def try_acquire(self, tokens: float = 1.0) -> bool:
        """Attempt to acquire tokens without blocking.

        Returns True if tokens were consumed, False if insufficient tokens.
        """
        if tokens <= 0:
            return True

        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def acquire(self, tokens: float = 1.0, timeout: Optional[float] = None) -> bool:
        """Acquire tokens, optionally blocking until available or timeout expires."""
        if tokens <= 0:
            return True

        start_time = time.time()
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True

                needed = tokens - self._tokens
                wait_seconds = needed / self.refill_rate

            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed + wait_seconds > timeout:
                    return False

            sleep_time = min(wait_seconds, 0.05)
            time.sleep(sleep_time)

    def reset(self) -> None:
        """Restore bucket to full capacity."""
        with self._lock:
            self._tokens = self.capacity
            self._last_refill = time.time()
