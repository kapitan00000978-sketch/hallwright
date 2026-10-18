"""
Hallwright Enterprise Resilience: Flow Control & Backpressure Engine.
Part of Pillar IV: Enterprise Modular Domain Libraries (Bosqich 53).

Implements Token Bucket and Leaky Bucket algorithms to protect downstream services
from overload and prevent queue saturation.
"""

import time
import threading
from typing import Optional


class BackpressureExceeded(Exception):
    """Raised when backpressure reject policy drops a request due to saturation."""
    pass


class TokenBucketLimiter:
    """
    Thread-safe Token Bucket rate limiter and flow controller.
    Allows bursts up to capacity while constraining long-term rate to refill_rate.
    """

    def __init__(self, capacity: float, refill_rate: float):
        if capacity <= 0 or refill_rate <= 0:
            raise ValueError("Capacity and refill_rate must be positive.")
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity)
        self.last_update = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self, now: float) -> None:
        elapsed = now - self.last_update
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_update = now

    def acquire(self, tokens: float = 1.0, blocking: bool = False, timeout: Optional[float] = None) -> bool:
        """Attempts to consume tokens. Returns True if granted, False otherwise."""
        start = time.monotonic()
        while True:
            with self._lock:
                now = time.monotonic()
                self._refill(now)
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True

            if not blocking:
                return False

            if timeout is not None and (time.monotonic() - start) >= timeout:
                return False

            time.sleep(0.005)


class LeakyBucketQueue:
    """
    Leaky Bucket queue that absorbs traffic bursts and drains at a smooth, constant rate.
    """

    def __init__(self, capacity: int, leak_rate: float):
        self.capacity = max(1, capacity)
        self.leak_rate = max(0.1, leak_rate)
        self.water_level = 0.0
        self.last_leak = time.monotonic()
        self._lock = threading.Lock()

    def _leak(self, now: float) -> None:
        elapsed = now - self.last_leak
        self.water_level = max(0.0, self.water_level - elapsed * self.leak_rate)
        self.last_leak = now

    def add(self, amount: float = 1.0) -> bool:
        """Returns True if bucket had space, False if backpressure dropped the request."""
        with self._lock:
            now = time.monotonic()
            self._leak(now)
            if self.water_level + amount <= self.capacity:
                self.water_level += amount
                return True
            return False
