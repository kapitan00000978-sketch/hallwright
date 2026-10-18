"""Hallwright Enterprise Performance Library: Single-Producer Single-Consumer (SPSC) Ring Buffer.

Provides a fixed-size, zero-allocation circular buffer optimized for high-throughput
pipelining between concurrent worker threads without dynamic heap allocations.
"""

from typing import Generic, TypeVar, Optional, List
import threading


T = TypeVar("T")


class RingBufferFullError(Exception):
    """Raised when pushing to a full non-overwriting ring buffer."""
    pass


class RingBufferEmptyError(Exception):
    """Raised when popping from an empty ring buffer."""
    pass


class SPSCRingBuffer(Generic[T]):
    """High-performance circular ring buffer for streaming workflows.

    Features:
    - Fixed pre-allocated slot memory (zero GC pressure in steady state)
    - Optional overwrite-on-overflow mode (ring mode) or strict rejection
    - Fast batch read and write methods
    - Thread-safe head and tail management
    """

    def __init__(self, capacity: int, overwrite_on_full: bool = False):
        if capacity <= 0:
            raise ValueError("Ring buffer capacity must be strictly greater than 0.")
        self.capacity: int = capacity
        self.overwrite_on_full: bool = overwrite_on_full

        # Pre-allocate slot array
        self._slots: List[Optional[T]] = [None] * capacity
        self._head: int = 0  # Read pointer
        self._tail: int = 0  # Write pointer
        self._size: int = 0
        self._lock = threading.Lock()

    @property
    def size(self) -> int:
        """Return the current number of elements in the buffer."""
        with self._lock:
            return self._size

    @property
    def is_empty(self) -> bool:
        """Check if buffer has zero items."""
        with self._lock:
            return self._size == 0

    @property
    def is_full(self) -> bool:
        """Check if buffer is at maximum capacity."""
        with self._lock:
            return self._size == self.capacity

    def push(self, item: T) -> bool:
        """Insert an item at the tail of the buffer.

        Returns True on success. If buffer is full and overwrite_on_full is False,
        raises RingBufferFullError.
        """
        with self._lock:
            if self._size == self.capacity:
                if not self.overwrite_on_full:
                    raise RingBufferFullError(f"RingBuffer is at full capacity ({self.capacity}).")
                # Advance head to overwrite the oldest item
                self._head = (self._head + 1) % self.capacity
                self._size -= 1

            self._slots[self._tail] = item
            self._tail = (self._tail + 1) % self.capacity
            self._size += 1
            return True

    def pop(self) -> T:
        """Remove and return the oldest item from the head of the buffer.

        Raises RingBufferEmptyError if empty.
        """
        with self._lock:
            if self._size == 0:
                raise RingBufferEmptyError("RingBuffer is empty.")

            item = self._slots[self._head]
            self._slots[self._head] = None  # Clear reference for GC
            self._head = (self._head + 1) % self.capacity
            self._size -= 1
            return item  # type: ignore

    def peek(self) -> Optional[T]:
        """Inspect the oldest item without removing it."""
        with self._lock:
            if self._size == 0:
                return None
            return self._slots[self._head]

    def clear(self) -> None:
        """Reset the buffer to empty state."""
        with self._lock:
            self._slots = [None] * self.capacity
            self._head = 0
            self._tail = 0
            self._size = 0
