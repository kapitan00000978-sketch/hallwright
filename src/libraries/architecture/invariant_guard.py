"""
Hallwright Enterprise Architecture: Domain Invariant Guard.
Part of Pillar IV: Enterprise Modular Domain Libraries (Bosqich 42).

Enforces clean architectural boundaries, non-negotiable invariants,
and domain contracts across system components with zero external dependencies.
"""

from typing import Callable, Any, Optional, List, Dict
from dataclasses import dataclass, field
import functools
import logging

logger = logging.getLogger("hallwright.invariant")


class InvariantViolation(Exception):
    """Raised when an architectural or domain invariant contract is breached."""
    def __init__(self, rule_name: str, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(f"Invariant '{rule_name}' violated: {message}")
        self.rule_name = rule_name
        self.message = message
        self.context = context or {}


@dataclass
class InvariantResult:
    passed: bool
    rule_name: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)


class InvariantGuard:
    """
    Central registry and enforcer for system invariants.
    Supports both assertion guards and soft diagnostic evaluations.
    """

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self._invariants: Dict[str, Callable[..., bool]] = {}
        self._violations: List[InvariantResult] = []

    def register(self, rule_name: str, predicate: Callable[..., bool]) -> None:
        """Registers a named invariant validation rule."""
        self._invariants[rule_name] = predicate

    def check(self, rule_name: str, *args, message: str = "", context: Optional[Dict[str, Any]] = None, **kwargs) -> InvariantResult:
        """Evaluates an invariant rule against the supplied arguments."""
        if rule_name not in self._invariants:
            raise KeyError(f"Invariant rule '{rule_name}' is not registered.")

        predicate = self._invariants[rule_name]
        try:
            passed = bool(predicate(*args, **kwargs))
        except Exception as exc:
            passed = False
            message = message or f"Predicate raised exception: {exc}"

        msg = message or ("Invariant preserved" if passed else "Condition not met")
        res = InvariantResult(passed=passed, rule_name=rule_name, message=msg, context=context or {})

        if not passed:
            self._violations.append(res)
            logger.warning("Invariant violation: %s (%s)", rule_name, msg)
            if self.strict_mode:
                raise InvariantViolation(rule_name, msg, context)

        return res

    def require(self, condition: bool, rule_name: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Direct inline invariant assertion."""
        if not condition:
            res = InvariantResult(passed=False, rule_name=rule_name, message=message, context=context or {})
            self._violations.append(res)
            if self.strict_mode:
                raise InvariantViolation(rule_name, message, context)

    @property
    def violations(self) -> List[InvariantResult]:
        return list(self._violations)

    def clear_violations(self) -> None:
        self._violations.clear()


def invariant_required(rule_name: str, predicate: Callable[[Any], bool], message: str = ""):
    """Decorator for functions/methods enforcing an invariant on the return value."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            if not predicate(result):
                err_msg = message or f"Function '{fn.__name__}' returned value violating invariant '{rule_name}'"
                raise InvariantViolation(rule_name, err_msg, {"function": fn.__name__, "return_value": repr(result)[:200]})
            return result
        return wrapper
    return decorator
