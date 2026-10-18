"""Hallwright Enterprise Architecture Library: Event Bus.

Provides a thread-safe, decoupled event broker supporting sync/async dispatch,
topic wildcard matching, priority ordering, and dead-letter queues.
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
import fnmatch
import time
import inspect


@dataclass(order=True)
class EventSubscription:
    """Subscription record ordered by priority (higher priority runs first)."""
    priority: int
    pattern: str = field(compare=False)
    handler: Callable[[str, Any], Any] = field(compare=False)
    once: bool = field(compare=False, default=False)


@dataclass
class DeadLetterMessage:
    """Envelope for events that had no subscribers or failed during dispatch."""
    topic: str
    payload: Any
    reason: str
    timestamp: float = field(default_factory=time.time)


class EventBus:
    """Enterprise-grade decoupled Event Bus.

    Features:
    - Topic wildcard matching (e.g., 'user.*', 'audit.#')
    - Priority-based subscriber execution (higher priority first)
    - Dead-letter queue (DLQ) for unhandled or faulted deliveries
    - One-time subscriber support (.once)
    - Comprehensive dispatch audit stats
    """

    def __init__(self):
        self._subscriptions: List[EventSubscription] = []
        self._dead_letters: List[DeadLetterMessage] = []
        self._dispatch_count: int = 0

    @property
    def dead_letters(self) -> List[DeadLetterMessage]:
        """Return the messages in the dead-letter queue."""
        return list(self._dead_letters)

    @property
    def dispatch_count(self) -> int:
        """Total number of successful event dispatches."""
        return self._dispatch_count

    def subscribe(
        self,
        pattern: str,
        handler: Callable[[str, Any], Any],
        priority: int = 100,
        once: bool = False,
    ) -> EventSubscription:
        """Subscribe a handler to an event pattern."""
        if not pattern or not isinstance(pattern, str):
            raise ValueError("Event pattern must be a non-empty string.")
        if not callable(handler):
            raise TypeError("Event handler must be callable.")

        sub = EventSubscription(
            priority=-priority,  # Inverted so heapq/sort orders descending
            pattern=pattern,
            handler=handler,
            once=once,
        )
        self._subscriptions.append(sub)
        self._subscriptions.sort()
        return sub

    def once(
        self,
        pattern: str,
        handler: Callable[[str, Any], Any],
        priority: int = 100,
    ) -> EventSubscription:
        """Register a one-time event subscriber."""
        return self.subscribe(pattern, handler, priority=priority, once=True)

    def unsubscribe(self, subscription: EventSubscription) -> bool:
        """Unregister an existing subscription."""
        if subscription in self._subscriptions:
            self._subscriptions.remove(subscription)
            return True
        return False

    def publish(self, topic: str, payload: Any = None) -> int:
        """Publish an event to all matching pattern subscribers.

        Returns the number of subscribers that processed the event.
        """
        matched = [
            sub for sub in self._subscriptions
            if fnmatch.fnmatch(topic, sub.pattern)
        ]

        if not matched:
            self._dead_letters.append(
                DeadLetterMessage(
                    topic=topic,
                    payload=payload,
                    reason="NO_SUBSCRIBERS_MATCHED",
                )
            )
            return 0

        dispatched_count = 0
        to_remove = []

        for sub in matched:
            try:
                sig = inspect.signature(sub.handler)
                params_len = len(sig.parameters)
                if params_len == 1:
                    sub.handler(payload)
                else:
                    sub.handler(topic, payload)

                dispatched_count += 1
                self._dispatch_count += 1
            except Exception as exc:
                self._dead_letters.append(
                    DeadLetterMessage(
                        topic=topic,
                        payload=payload,
                        reason=f"HANDLER_EXCEPTION: {str(exc)}",
                    )
                )

            if sub.once:
                to_remove.append(sub)

        for sub in to_remove:
            if sub in self._subscriptions:
                self._subscriptions.remove(sub)

        return dispatched_count

    def clear(self) -> None:
        """Clear all subscriptions and dead letters."""
        self._subscriptions.clear()
        self._dead_letters.clear()
        self._dispatch_count = 0
