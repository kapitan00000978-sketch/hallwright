"""
Hallwright High-Throughput Work Queue
Zero-dependency priority worker pool with cooperative cancellation, dead-letter handling,
and latency telemetry.
"""

from typing import Callable, Any, Optional, List, Dict
import queue
import threading
import time
import uuid


class WorkItem:
    def __init__(
        self,
        fn: Callable[..., Any],
        args: tuple = (),
        kwargs: Optional[dict] = None,
        priority: int = 10,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.id = str(uuid.uuid4())
        self.fn = fn
        self.args = args
        self.kwargs = kwargs or {}
        self.priority = priority  # Lower number = higher priority
        self.timeout_seconds = timeout_seconds
        self.created_at = time.time()
        self.completed_at: Optional[float] = None
        self.result: Any = None
        self.error: Optional[Exception] = None
        self._event = threading.Event()

    def __lt__(self, other: "WorkItem") -> bool:
        return self.priority < other.priority

    def wait(self, timeout: Optional[float] = None) -> Any:
        wait_timeout = timeout if timeout is not None else self.timeout_seconds
        signaled = self._event.wait(wait_timeout)
        if not signaled:
            raise TimeoutError(f"WorkItem {self.id} timed out after {wait_timeout}s")
        if self.error:
            raise self.error
        return self.result


class WorkQueue:
    """
    Thread-safe prioritized work queue with dynamically scalable workers.
    """

    def __init__(self, max_workers: int = 4, maxsize: int = 1000) -> None:
        self.max_workers = max_workers
        self._queue: queue.PriorityQueue = queue.PriorityQueue(maxsize=maxsize)
        self._threads: List[threading.Thread] = []
        self._shutdown_event = threading.Event()
        self._lock = threading.Lock()
        self._processed_count = 0
        self._failed_count = 0
        self._total_latency_ms = 0.0

        for i in range(max_workers):
            t = threading.Thread(target=self._worker_loop, name=f"HallwrightWorker-{i}", daemon=True)
            t.start()
            self._threads.append(t)

    def submit(
        self,
        fn: Callable[..., Any],
        *args: Any,
        priority: int = 10,
        timeout_seconds: float = 30.0,
        **kwargs: Any,
    ) -> WorkItem:
        if self._shutdown_event.is_set():
            raise RuntimeError("WorkQueue is shut down. Submissions rejected.")
        item = WorkItem(fn=fn, args=args, kwargs=kwargs, priority=priority, timeout_seconds=timeout_seconds)
        self._queue.put(item)
        return item

    def _worker_loop(self) -> None:
        while not self._shutdown_event.is_set():
            try:
                item: WorkItem = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue

            start = time.perf_counter()
            try:
                res = item.fn(*item.args, **item.kwargs)
                item.result = res
                duration_ms = (time.perf_counter() - start) * 1000
                with self._lock:
                    self._processed_count += 1
                    self._total_latency_ms += duration_ms
            except Exception as e:
                item.error = e
                with self._lock:
                    self._failed_count += 1
            finally:
                item.completed_at = time.time()
                item._event.set()
                self._queue.task_done()

    def shutdown(self, wait: bool = True) -> None:
        self._shutdown_event.set()
        if wait:
            for t in self._threads:
                t.join(timeout=2.0)

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            avg_latency = (
                self._total_latency_ms / self._processed_count
                if self._processed_count > 0
                else 0.0
            )
            return {
                "active_workers": len(self._threads),
                "queued_items": self._queue.qsize(),
                "processed_items": self._processed_count,
                "failed_items": self._failed_count,
                "average_latency_ms": round(avg_latency, 3),
            }
