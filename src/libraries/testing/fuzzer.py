"""Hallwright Enterprise Testing Library: Property-Based Edge-Case Fuzzer.

Provides deterministic and pseudo-random fuzzing generators to uncover
boundary violations, null-pointer exceptions, and numeric overflow edge cases.
"""

import sys
import random
import string
from typing import List, Any, Callable, Dict
from dataclasses import dataclass


@dataclass
class FuzzFailure:
    """Represents a caught exception during fuzz testing."""
    iteration: int
    inputs: Any
    exception: str
    traceback: str


class EdgeCaseGenerator:
    """Generates boundary and adversarial inputs across common primitive types."""

    @staticmethod
    def boundary_integers() -> List[int]:
        """Exhaustive list of integer boundary and overflow values."""
        return [
            0, 1, -1,
            2**7 - 1, -(2**7),          # int8
            2**15 - 1, -(2**15),        # int16
            2**31 - 1, -(2**31),        # int32
            2**63 - 1, -(2**63),        # int64
            sys.maxsize, -sys.maxsize - 1,
        ]

    @staticmethod
    def boundary_floats() -> List[float]:
        """Exhaustive list of floating-point boundaries and special values."""
        return [
            0.0, -0.0, 1.0, -1.0,
            float("inf"), float("-inf"), float("nan"),
            sys.float_info.min, sys.float_info.max,
            sys.float_info.epsilon,
            1e-300, 1e300,
        ]

    @staticmethod
    def adversarial_strings() -> List[str]:
        """Adversarial string edge cases including null bytes, unicode escapes, and format injections."""
        return [
            "",
            " ",
            "\t\r\n",
            "\x00",
            "\x00\x00\x00",
            "A" * 1000,
            "A" * 10000,
            "🔥🚀👑⚡💎",
            "ñ, é, ö, ü, ç, å",
            "Владимир",
            "مرحبا",
            "こんにちは",
            "{{7*7}}",
            "${7*7}",
            "%s%s%s%s%s%s%s%s%n",
            "<script>alert(1)</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\cmd.exe",
        ]


class FuzzRunner:
    """Executes iterative fuzz testing against target functions."""

    @classmethod
    def fuzz(
        cls,
        func: Callable[..., Any],
        generator: Callable[[], Any],
        iterations: int = 100,
        expected_exceptions: tuple = (),
    ) -> List[FuzzFailure]:
        """Run fuzz iterations, returning any unexpected exceptions."""
        failures: List[FuzzFailure] = []

        for i in range(iterations):
            sample = generator()
            try:
                if isinstance(sample, tuple):
                    func(*sample)
                elif isinstance(sample, dict):
                    func(**sample)
                else:
                    func(sample)
            except expected_exceptions:
                continue
            except Exception as exc:
                failures.append(
                    FuzzFailure(
                        iteration=i,
                        inputs=sample,
                        exception=type(exc).__name__ + ": " + str(exc),
                        traceback="",
                    )
                )

        return failures
