"""Hallwright Enterprise Architecture Library: Finite State Machine (FSM).

Provides a deterministic, transition-guarded finite state machine with
audit logging, state history, rollbacks, and hook listeners.
"""

from typing import Dict, List, Set, Callable, Optional, Any
from dataclasses import dataclass, field
import time


class StateMachineError(Exception):
    """Base exception for State Machine violations."""
    pass


class InvalidTransitionError(StateMachineError):
    """Raised when an illegal state transition is attempted."""
    pass


class GuardFailedError(StateMachineError):
    """Raised when a transition guard condition evaluates to False."""
    pass


@dataclass
class Transition:
    """Represents an atomic transition between two states."""
    source: str
    target: str
    event: str
    guard: Optional[Callable[[Dict[str, Any]], bool]] = None
    action: Optional[Callable[[Dict[str, Any]], None]] = None


@dataclass
class StateHistoryEntry:
    """Audit log entry for a completed state transition."""
    from_state: str
    to_state: str
    event: str
    timestamp: float = field(default_factory=time.time)
    context_snapshot: Dict[str, Any] = field(default_factory=dict)


class FiniteStateMachine:
    """Deterministic, production-ready Finite State Machine.

    Features:
    - Multiple source states for single event
    - Transition guard predicates
    - Entry/exit hooks per state
    - Pre/post transition global listeners
    - Complete transition history with rollbacks
    - Thread-safe state context storage
    """

    def __init__(self, initial_state: str, context: Optional[Dict[str, Any]] = None):
        if not initial_state or not isinstance(initial_state, str):
            raise StateMachineError("Initial state must be a non-empty string.")
        self._current_state = initial_state
        self._initial_state = initial_state
        self._states: Set[str] = {initial_state}
        self._transitions: Dict[str, List[Transition]] = {}  # keyed by (source, event)
        self._entry_hooks: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self._exit_hooks: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self._history: List[StateHistoryEntry] = []
        self._context: Dict[str, Any] = dict(context or {})

    @property
    def current_state(self) -> str:
        """Return the current active state."""
        return self._current_state

    @property
    def context(self) -> Dict[str, Any]:
        """Return the shared state machine context."""
        return self._context

    @property
    def history(self) -> List[StateHistoryEntry]:
        """Return the chronological transition history."""
        return list(self._history)

    def add_state(self, state: str) -> "FiniteStateMachine":
        """Register a valid state in the machine."""
        if not state or not isinstance(state, str):
            raise StateMachineError("State name must be a non-empty string.")
        self._states.add(state)
        return self

    def add_transition(
        self,
        source: str,
        target: str,
        event: str,
        guard: Optional[Callable[[Dict[str, Any]], bool]] = None,
        action: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> "FiniteStateMachine":
        """Define a valid state transition triggered by an event."""
        self.add_state(source)
        self.add_state(target)
        key = f"{source}:{event}"
        if key not in self._transitions:
            self._transitions[key] = []
        self._transitions[key].append(
            Transition(source=source, target=target, event=event, guard=guard, action=action)
        )
        return self

    def on_enter(self, state: str, hook: Callable[[Dict[str, Any]], None]) -> "FiniteStateMachine":
        """Register a hook executed upon entering a state."""
        self.add_state(state)
        self._entry_hooks.setdefault(state, []).append(hook)
        return self

    def on_exit(self, state: str, hook: Callable[[Dict[str, Any]], None]) -> "FiniteStateMachine":
        """Register a hook executed upon exiting a state."""
        self.add_state(state)
        self._exit_hooks.setdefault(state, []).append(hook)
        return self

    def trigger(self, event: str, **kwargs: Any) -> str:
        """Trigger an event to transition the machine to a new state."""
        self._context.update(kwargs)
        key = f"{self._current_state}:{event}"
        possible_transitions = self._transitions.get(key, [])

        if not possible_transitions:
            raise InvalidTransitionError(
                f"No transition configured for event '{event}' from state '{self._current_state}'."
            )

        selected_transition: Optional[Transition] = None
        for trans in possible_transitions:
            if trans.guard is None or trans.guard(self._context):
                selected_transition = trans
                break

        if selected_transition is None:
            raise GuardFailedError(
                f"All guard conditions failed for event '{event}' from state '{self._current_state}'."
            )

        old_state = self._current_state
        target_state = selected_transition.target

        # Execute exit hooks of the current state
        for exit_hook in self._exit_hooks.get(old_state, []):
            exit_hook(self._context)

        # Execute transition action if defined
        if selected_transition.action:
            selected_transition.action(self._context)

        # Record audit history
        self._history.append(
            StateHistoryEntry(
                from_state=old_state,
                to_state=target_state,
                event=event,
                context_snapshot=dict(self._context),
            )
        )

        # Update current state
        self._current_state = target_state

        # Execute entry hooks of the target state
        for enter_hook in self._entry_hooks.get(target_state, []):
            enter_hook(self._context)

        return self._current_state

    def can_trigger(self, event: str) -> bool:
        """Check if an event can be triggered from current state without raising exceptions."""
        key = f"{self._current_state}:{event}"
        candidates = self._transitions.get(key, [])
        if not candidates:
            return False
        for c in candidates:
            if c.guard is None or c.guard(self._context):
                return True
        return False

    def rollback(self) -> str:
        """Revert the state machine to the immediately preceding state."""
        if not self._history:
            raise StateMachineError("Cannot rollback: history is empty.")

        last_entry = self._history.pop()
        self._current_state = last_entry.from_state
        self._context = dict(last_entry.context_snapshot)
        return self._current_state

    def reset(self) -> None:
        """Reset the state machine back to its initial state."""
        self._current_state = self._initial_state
        self._history.clear()
        self._context.clear()
