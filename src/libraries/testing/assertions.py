"""Hallwright Enterprise Testing Library: Fluent Assertion Suite.

Provides expressive, readable, and diagnostic assertion helpers with
actionable failure messages and structured diff formatting.
"""

from typing import Any, Type, Pattern
import re


class FluentAssertionError(AssertionError):
    """Raised when a fluent assertion expectation is violated."""
    pass


class AssertThat:
    """Fluent assertion wrapper providing readable chaining syntax."""

    def __init__(self, actual: Any):
        self.actual = actual

    def is_equal_to(self, expected: Any, message: str = "") -> "AssertThat":
        """Assert that actual is strictly equal to expected."""
        if self.actual != expected:
            msg = message or f"Expected <{expected!r}>, but got <{self.actual!r}>."
            raise FluentAssertionError(msg)
        return self

    def is_not_equal_to(self, expected: Any, message: str = "") -> "AssertThat":
        """Assert that actual is not equal to expected."""
        if self.actual == expected:
            msg = message or f"Expected value to NOT equal <{expected!r}>, but it did."
            raise FluentAssertionError(msg)
        return self

    def is_none(self, message: str = "") -> "AssertThat":
        """Assert that actual is None."""
        if self.actual is not None:
            msg = message or f"Expected None, but got <{self.actual!r}>."
            raise FluentAssertionError(msg)
        return self

    def is_not_none(self, message: str = "") -> "AssertThat":
        """Assert that actual is not None."""
        if self.actual is None:
            msg = message or "Expected a non-None value, but got None."
            raise FluentAssertionError(msg)
        return self

    def is_true(self, message: str = "") -> "AssertThat":
        """Assert that actual evaluates to True."""
        if not bool(self.actual):
            msg = message or f"Expected True expression, but got <{self.actual!r}>."
            raise FluentAssertionError(msg)
        return self

    def is_false(self, message: str = "") -> "AssertThat":
        """Assert that actual evaluates to False."""
        if bool(self.actual):
            msg = message or f"Expected False expression, but got <{self.actual!r}>."
            raise FluentAssertionError(msg)
        return self

    def is_instance_of(self, expected_type: Type, message: str = "") -> "AssertThat":
        """Assert that actual is an instance of the specified type."""
        if not isinstance(self.actual, expected_type):
            msg = message or f"Expected instance of <{expected_type.__name__}>, but got <{type(self.actual).__name__}>."
            raise FluentAssertionError(msg)
        return self

    def contains(self, item: Any, message: str = "") -> "AssertThat":
        """Assert that the collection or string contains the item."""
        try:
            if item not in self.actual:
                msg = message or f"Expected <{self.actual!r}> to contain <{item!r}>."
                raise FluentAssertionError(msg)
        except TypeError as exc:
            raise FluentAssertionError(f"Target object is not iterable: {str(exc)}")
        return self

    def has_length(self, length: int, message: str = "") -> "AssertThat":
        """Assert that the collection has the exact specified length."""
        actual_len = len(self.actual)
        if actual_len != length:
            msg = message or f"Expected length {length}, but got {actual_len}."
            raise FluentAssertionError(msg)
        return self

    def matches_regex(self, pattern: str, message: str = "") -> "AssertThat":
        """Assert that the string matches the regex pattern."""
        if not isinstance(self.actual, str):
            raise FluentAssertionError(f"Target is not a string: {type(self.actual).__name__}")
        if not re.search(pattern, self.actual):
            msg = message or f"Expected string <{self.actual!r}> to match regex <{pattern}>."
            raise FluentAssertionError(msg)
        return self

    def is_between(self, lower: Any, upper: Any, inclusive: bool = True, message: str = "") -> "AssertThat":
        """Assert that a numeric value lies within bounds."""
        if inclusive:
            valid = lower <= self.actual <= upper
        else:
            valid = lower < self.actual < upper

        if not valid:
            msg = message or f"Expected {self.actual} to be between [{lower}, {upper}]."
            raise FluentAssertionError(msg)
        return self


def assert_that(actual: Any) -> AssertThat:
    """Entrypoint to fluent assertion chains."""
    return AssertThat(actual)
