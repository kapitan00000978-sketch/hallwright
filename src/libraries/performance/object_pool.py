"""Hallwright Enterprise Performance Library: Generic Object Pool.

Provides thread-safe object reuse for high-allocation subsystems, eliminating
garbage collection pauses by recycling expensive connection handles and data buffers.
"""

from typing import Generic, TypeVar, Callable, Optional, List
import threading
from contextlib import contextmanager


T = TypeVar("T")


class ObjectPoolExhaustedError(Exception):
    """Raised when the pool is depleted and max_capacity is reached."""
    pass


class ObjectPool(Generic[T]):
    """Thread-safe generic Object Pool.

    Features:
    - Factory function for on-demand object creation
    - Optional reset/cleanup callback upon return
    - Pre-warming to prime instances in advance
    - Context manager interface for safe RAII borrow/return
    - Capacity constraints with overflow defense
    """

    def __init__(
        self,
        factory: Callable[[], T],
        reset_fn: Optional[Callable[[T], None]] = None,
        initial_size: int = 5,
        max_capacity: int = 50,
    ):
        if not callable(factory):
            raise TypeError("Object pool factory must be callable.")
        if max_capacity < initial_size:
            raise ValueError("max_capacity cannot be less than initial_size.")

        self._factory: Callable[[], T] = factory
        self._reset_fn: Optional[Callable[[T], None]] = reset_fn
        self._max_capacity: int = max_capacity
        self._available: List[T] = []
        self._created_count: int = 0
        self._lock: threading.Lock = threading.Lock()

        # Pre-warm
        for _ in range(initial_size):
            obj = self._factory()
            self._available.append(obj)
            self._created_count += 1

    @property
    def available_count(self) -> int:
        """Number of idle objects ready for immediate borrow."""
        with self._lock:
            return len(self._available)

    @property
    def total_created(self) -> int:
        """Total count of instances created by this pool."""
        with self._lock:
            return self._created_count

    def borrow(self) -> T:
        """Acquire an object from the pool, instantiating a new one if permitted."""
        with self._lock:
            if self._available:
                return self._available.pop()

            if self._created_count < self._max_capacity:
                obj = self._factory()
                self._created_count += 1
                return obj

            raise ObjectPoolExhaustedError(
                f"Object pool exhausted: maximum capacity of {self._max_capacity} reached."
            )

    def release(self, obj: T) -> None:
        """Return an object to the pool, invoking reset callback if configured."""
        if self._reset_fn:
            try:
                self._reset_fn(obj)
            except Exception:
                # Do not re-pool corrupted object
                with self._lock:
                    self._created_count -= 1
                return

        with self._lock:
            if len(self._available) < self._max_capacity:
                self._available.append(obj)
            else:
                self._created_count -= 1

    @contextmanager
    def acquire(self):
        """Context manager for automatic borrowing and returning of an object."""
        obj = self.borrow()
        try:
            yield obj
        finally:
            self.release(obj)
