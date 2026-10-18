"""Hallwright Architecture Library.

Exposes production-grade design pattern implementations:
- FiniteStateMachine: Deterministic guarded state machine with history & rollback
- EventBus: Topic-based decoupled event broker with wildcard patterns & DLQ
- CircuitBreaker: Distributed call fault tolerance & self-healing
- Ports & Entities: Clean / Hexagonal architecture base classes
"""

from .fsm import (
    FiniteStateMachine,
    Transition,
    StateHistoryEntry,
    StateMachineError,
    InvalidTransitionError,
    GuardFailedError,
)
from .event_bus import (
    EventBus,
    EventSubscription,
    DeadLetterMessage,
)
from .circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerOpenException,
)
from .ports import (
    BaseEntity,
    ValueObject,
    AggregateRoot,
    RepositoryPort,
    UnitOfWorkPort,
)
from .outbox_pattern import (
    TransactionalOutbox,
    OutboxRecord,
    OutboxStatus,
)
from .invariant_guard import (
    InvariantGuard,
    InvariantViolation,
    invariant_required,
)
from .saga_coordinator import (
    SagaCoordinator,
    SagaStep,
    SagaStepStatus,
    SagaState,
)

__all__ = [
    "FiniteStateMachine",
    "Transition",
    "StateHistoryEntry",
    "StateMachineError",
    "InvalidTransitionError",
    "GuardFailedError",
    "EventBus",
    "EventSubscription",
    "DeadLetterMessage",
    "CircuitBreaker",
    "CircuitState",
    "CircuitBreakerOpenException",
    "BaseEntity",
    "ValueObject",
    "AggregateRoot",
    "RepositoryPort",
    "UnitOfWorkPort",
    "TransactionalOutbox",
    "OutboxRecord",
    "OutboxStatus",
    "InvariantGuard",
    "InvariantViolation",
    "invariant_required",
    "SagaCoordinator",
    "SagaStep",
    "SagaStepStatus",
    "SagaState",
]
