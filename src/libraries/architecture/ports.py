"""Hallwright Enterprise Architecture Library: Clean Architecture Ports & Entities.

Provides domain modeling abstractions (Entities, Value Objects, Aggregate Roots)
and Hexagonal Architecture Port definitions (RepositoryPort, UnitOfWork).
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Dict, Any
from dataclasses import dataclass, field
import uuid
import time


TId = TypeVar("TId")
TEntity = TypeVar("TEntity", bound="BaseEntity")


@dataclass(frozen=True)
class ValueObject(ABC):
    """Immutable domain Value Object with structural equality."""
    pass


class BaseEntity(Generic[TId]):
    """Domain Entity with unique identity lifecycle."""

    def __init__(self, id: TId):
        if id is None:
            raise ValueError("Entity ID cannot be None.")
        self._id: TId = id
        self._created_at: float = time.time()
        self._version: int = 1

    @property
    def id(self) -> TId:
        return self._id

    @property
    def created_at(self) -> float:
        return self._created_at

    @property
    def version(self) -> int:
        return self._version

    def increment_version(self) -> None:
        self._version += 1

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((self.__class__, self._id))


class AggregateRoot(BaseEntity[TId]):
    """Aggregate Root managing domain events and transactional consistency boundary."""

    def __init__(self, id: TId):
        super().__init__(id)
        self._domain_events: List[Dict[str, Any]] = []

    def record_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Stage a domain event to be dispatched when the aggregate is persisted."""
        self._domain_events.append({
            "event_id": str(uuid.uuid4()),
            "aggregate_id": str(self.id),
            "type": event_type,
            "occurred_at": time.time(),
            "payload": payload,
        })

    def pull_domain_events(self) -> List[Dict[str, Any]]:
        """Extract and clear all staged domain events."""
        events = list(self._domain_events)
        self._domain_events.clear()
        return events


class RepositoryPort(ABC, Generic[TEntity, TId]):
    """Outbound Port for persisting and retrieving domain aggregates."""

    @abstractmethod
    def get_by_id(self, entity_id: TId) -> Optional[TEntity]:
        """Retrieve entity by unique identifier."""
        raise NotImplementedError

    @abstractmethod
    def save(self, entity: TEntity) -> None:
        """Persist entity state."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: TId) -> bool:
        """Remove entity by identifier."""
        raise NotImplementedError

    @abstractmethod
    def list_all(self, limit: int = 100, offset: int = 0) -> List[TEntity]:
        """List entities with pagination."""
        raise NotImplementedError


class UnitOfWorkPort(ABC):
    """Outbound Port for transactional boundaries across multiple repositories."""

    @abstractmethod
    def __enter__(self) -> "UnitOfWorkPort":
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError
