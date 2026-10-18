"""Hallwright Enterprise Performance Library.

Exposes high-throughput components:
- LRUCache, cached: Thread-safe O(1) LRU & TTL cache with hit-ratio metrics
- SPSCRingBuffer: Single-producer single-consumer circular buffer with zero GC allocations
- ObjectPool: Thread-safe pre-warmed object recycler with RAII context manager
"""

from .cache import (
    LRUCache,
    cached,
)
from .ring_buffer import (
    SPSCRingBuffer,
    RingBufferFullError,
    RingBufferEmptyError,
)
from .object_pool import (
    ObjectPool,
    ObjectPoolExhaustedError,
)
from .work_queue import (
    WorkQueue,
    WorkItem,
)

__all__ = [
    "LRUCache",
    "cached",
    "SPSCRingBuffer",
    "RingBufferFullError",
    "RingBufferEmptyError",
    "ObjectPool",
    "ObjectPoolExhaustedError",
    "WorkQueue",
    "WorkItem",
]
