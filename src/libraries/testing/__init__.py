"""Hallwright Enterprise Testing Library.

Exposes test engineering components:
- EdgeCaseGenerator, FuzzRunner: Property-based edge case & boundary fuzzer
- assert_that, AssertThat: Fluent, readable assertion chains
- ASTMutationGenerator, CodeMutant: Synthetic AST code mutation test harness
"""

from .fuzzer import (
    EdgeCaseGenerator,
    FuzzRunner,
    FuzzFailure,
)
from .assertions import (
    assert_that,
    AssertThat,
    FluentAssertionError,
)
from .mutation_suite import (
    ASTMutationGenerator,
    CodeMutant,
)

__all__ = [
    "EdgeCaseGenerator",
    "FuzzRunner",
    "FuzzFailure",
    "assert_that",
    "AssertThat",
    "FluentAssertionError",
    "ASTMutationGenerator",
    "CodeMutant",
]
