"""Hallwright Enterprise Testing Library: AST Mutation Testing Harness.

Generates synthetic programmatic mutants by systematically altering AST nodes
(operators, comparison guards, booleans) to measure test suite killing fidelity.
"""

import ast
import copy
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class CodeMutant:
    """Represents an atomic syntax mutation."""
    id: str
    original_code: str
    mutated_code: str
    line: int
    description: str


class ASTMutationGenerator(ast.NodeTransformer):
    """Systematically swaps operators to generate valid mutant ASTs."""

    # Invert comparison operators
    _COMP_MAP = {
        ast.Eq: ast.NotEq,
        ast.NotEq: ast.Eq,
        ast.Lt: ast.GtE,
        ast.LtE: ast.Gt,
        ast.Gt: ast.LtE,
        ast.GtE: ast.Lt,
        ast.Is: ast.IsNot,
        ast.IsNot: ast.Is,
    }

    # Invert binary operators
    _BINOP_MAP = {
        ast.Add: ast.Sub,
        ast.Sub: ast.Add,
        ast.Mult: ast.FloorDiv,
    }

    @classmethod
    def generate_mutants(cls, source_code: str) -> List[CodeMutant]:
        """Analyze source code and yield all possible atomic mutated code variants."""
        mutants: List[CodeMutant] = []
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return mutants

        mutant_index = 0

        # Scan for mutable nodes
        for node in ast.walk(tree):
            # Mutate Comparisons
            if isinstance(node, ast.Compare):
                for idx, op in enumerate(node.ops):
                    op_type = type(op)
                    if op_type in cls._COMP_MAP:
                        new_tree = copy.deepcopy(tree)
                        # Locate corresponding node in copy
                        for target in ast.walk(new_tree):
                            if (
                                isinstance(target, ast.Compare)
                                and target.lineno == node.lineno
                                and target.col_offset == node.col_offset
                            ):
                                replacement_class = cls._COMP_MAP[op_type]
                                target.ops[idx] = replacement_class()
                                mutant_index += 1
                                mutants.append(
                                    CodeMutant(
                                        id=f"MUT-{mutant_index:03d}",
                                        original_code=source_code,
                                        mutated_code=ast.unparse(new_tree),
                                        line=node.lineno,
                                        description=f"Inverted comparison operator at line {node.lineno}.",
                                    )
                                )

            # Mutate Booleans (True <-> False)
            elif isinstance(node, ast.Constant) and isinstance(node.value, bool):
                new_tree = copy.deepcopy(tree)
                for target in ast.walk(new_tree):
                    if (
                        isinstance(target, ast.Constant)
                        and target.value == node.value
                        and getattr(target, "lineno", -1) == getattr(node, "lineno", -1)
                        and getattr(target, "col_offset", -1) == getattr(node, "col_offset", -1)
                    ):
                        target.value = not node.value
                        mutant_index += 1
                        mutants.append(
                            CodeMutant(
                                id=f"MUT-{mutant_index:03d}",
                                original_code=source_code,
                                mutated_code=ast.unparse(new_tree),
                                line=getattr(node, "lineno", 1),
                                description=f"Flipped boolean constant to {not node.value} at line {getattr(node, 'lineno', 1)}.",
                            )
                        )

        return mutants
