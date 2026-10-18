"""Hallwright Enterprise Performance Library: High-Concurrency Cache.

Provides LRU (Least Recently Used) and TTL-aware in-memory caching with
thread-safety, hit/miss telemetry, and clean decorator ergonomics.
"""

from typing import Dict, Any, Optional, Callable, Tuple
from collections import OrderedDict
import time
import threading
from functools import wraps


class LRUCache:
    """Thread-safe Least Recently Used (LRU) Cache with Time-To-Live (TTL).

    Features:
    - O(1) average time complexity for get, set, delete
    - Per-entry or default TTL expiration
    - Hit and Miss telemetry metrics
    - Thread-safe operations via reentrant lock
    - Max size eviction based on access recency
    """

    def __init__(self, max_size: int = 1000, default_ttl_sec: Optional[float] = None):
        if max_size <= 0:
            raise ValueError("max_size must be greater than 0.")
        self.max_size = max_size
        self.default_ttl_sec = default_ttl_sec

        self._store: OrderedDict[Any, Tuple[Any, Optional[float]]] = OrderedDict()
        self._lock = threading.RLock()

        self._hits = 0
        self._misses = 0
        self._evictions = 0

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    @property
    def evictions(self) -> int:
        return self._evictions

    @property
    def hit_ratio(self) -> float:
        total = self._hits + self._misses
        return (self._hits / total) if total > 0 else 0.0

    def get(self, key: Any, default: Any = None) -> Any:
        """Retrieve an item from the cache, updating its recency."""
        with self._lock:
            if key not in self._store:
                self._misses += 1
                return default

            value, expiry = self._store[key]

            # Check TTL
            if expiry is not None and time.time() > expiry:
                del self._store[key]
                self._misses += 1
                return default

            # Move to end (most recently used)
            self._store.move_to_end(key)
            self._hits += 1
            return value

    def set(self, key: Any, value: Any, ttl_sec: Optional[float] = None) -> None:
        """Insert or update an item in the cache."""
        with self._lock:
            ttl = ttl_sec if ttl_sec is not None else self.default_ttl_sec
            expiry = (time.time() + ttl) if ttl is not None else None

            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = (value, expiry)

            # Evict least recently used if exceeding capacity
            if len(self._store) > self.max_size:
                self._store.popitem(last=False)
                self._evictions += 1

    def delete(self, key: Any) -> bool:
        """Remove a specific key from cache."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def clear(self) -> None:
        """Purge all entries from the cache."""
        with self._lock:
            self._store.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._store)


def cached(cache_instance: Optional[LRUCache] = None, max_size: int = 256, ttl_sec: Optional[float] = None) -> Callable:
    """Decorator to cache function results using an LRUCache instance."""
    active_cache = cache_instance or LRUCache(max_size=max_size, default_ttl_sec=ttl_sec)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create a deterministic cache key from arguments
            key = (args, tuple(sorted(kwargs.items())))
            val = active_cache.get(key)
            if val is not None:
                return val
            result = func(*args, **kwargs)
            active_cache.set(key, result, ttl_sec=ttl_sec)
            return result

        wrapper.cache = active_cache  # type: ignore
        return wrapper

    return decorator
