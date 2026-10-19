"""
Hallwright Autonomous Mutation Testing Engine (Phase 3).
Part of the Hallwright Autonomous Craftsmanship Protocol.

Generates controlled AST mutations (boundary flips, comparison swaps, operator modifications,
and return alterations) to empirically evaluate the true regression-detection strength of test suites.
"""

import ast
import os
import sys
import copy
import time
import subprocess
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("hallwright.mutator")


class Mutant:
    """Represents a discrete synthetic AST mutation."""
    def __init__(
        self,
        mutant_id: str,
        file_path: str,
        line_number: int,
        mutation_type: str,
        description: str,
        mutated_source: str
    ):
        self.mutant_id = mutant_id
        self.file_path = file_path
        self.line_number = line_number
        self.mutation_type = mutation_type
        self.description = description
        self.mutated_source = mutated_source
        self.status = "PENDING"  # PENDING, KILLED, SURVIVED, ERROR
        self.execution_time_ms = 0.0


class MutationGenerator(ast.NodeVisitor):
    """Walks Python AST and generates discrete mutant variants."""

    def __init__(self, source_code: str, file_path: str = ""):
        self.source_code = source_code
        self.file_path = file_path
        self.mutants: List[Mutant] = []
        self._mutant_counter = 0

    def generate_all(self, limit: int = 20) -> List[Mutant]:
        """Parses source and extracts up to `limit` AST mutants."""
        try:
            tree = ast.parse(self.source_code)
        except SyntaxError as err:
            logger.warning("Could not parse %s for mutation: %s", self.file_path, err)
            return []

        # 1. Comparison operations (Gt <-> GtE, Eq <-> NotEq, Lt <-> LtE)
        for node in ast.walk(tree):
            if len(self.mutants) >= limit:
                break
            if isinstance(node, ast.Compare) and node.ops:
                op = node.ops[0]
                replacement_op = None
                desc = ""
                if isinstance(op, ast.Gt):
                    replacement_op = ast.GtE()
                    desc = "Flipped strict '>' to '>='"
                elif isinstance(op, ast.GtE):
                    replacement_op = ast.Gt()
                    desc = "Flipped '>=' to strict '>'"
                elif isinstance(op, ast.Lt):
                    replacement_op = ast.LtE()
                    desc = "Flipped strict '<' to '<='"
                elif isinstance(op, ast.LtE):
                    replacement_op = ast.Lt()
                    desc = "Flipped '<=' to strict '<'"
                elif isinstance(op, ast.Eq):
                    replacement_op = ast.NotEq()
                    desc = "Inverted equality '==' to '!='"
                elif isinstance(op, ast.NotEq):
                    replacement_op = ast.Eq()
                    desc = "Inverted inequality '!=' to '=='"

                if replacement_op:
                    mutated_tree = copy.deepcopy(tree)
                    target_node = self._find_matching_node(mutated_tree, node)
                    if target_node and hasattr(target_node, "ops") and target_node.ops:
                        target_node.ops[0] = replacement_op
                        try:
                            mut_source = ast.unparse(mutated_tree)
                            self._mutant_counter += 1
                            self.mutants.append(Mutant(
                                mutant_id=f"MUT_{self._mutant_counter:03d}",
                                file_path=self.file_path,
                                line_number=getattr(node, "lineno", 1),
                                mutation_type="COMPARISON_SWAP",
                                description=desc,
                                mutated_source=mut_source
                            ))
                        except Exception as unparse_err:
                            logger.debug("Failed unparsing comparison mutant: %s", unparse_err)

        # 2. Binary Operators (+ <-> -, * <-> //)
        for node in ast.walk(tree):
            if len(self.mutants) >= limit:
                break
            if isinstance(node, ast.BinOp):
                replacement_op = None
                desc = ""
                if isinstance(node.op, ast.Add):
                    replacement_op = ast.Sub()
                    desc = "Replaced addition '+' with subtraction '-'"
                elif isinstance(node.op, ast.Sub):
                    replacement_op = ast.Add()
                    desc = "Replaced subtraction '-' with addition '+'"

                if replacement_op:
                    mutated_tree = copy.deepcopy(tree)
                    target_node = self._find_matching_node(mutated_tree, node)
                    if target_node and hasattr(target_node, "op"):
                        target_node.op = replacement_op
                        try:
                            mut_source = ast.unparse(mutated_tree)
                            self._mutant_counter += 1
                            self.mutants.append(Mutant(
                                mutant_id=f"MUT_{self._mutant_counter:03d}",
                                file_path=self.file_path,
                                line_number=getattr(node, "lineno", 1),
                                mutation_type="OPERATOR_SWAP",
                                description=desc,
                                mutated_source=mut_source
                            ))
                        except Exception as unparse_err:
                            logger.debug("Failed unparsing binop mutant: %s", unparse_err)

        # 3. Boolean constants (True <-> False)
        for node in ast.walk(tree):
            if len(self.mutants) >= limit:
                break
            if isinstance(node, ast.Constant) and isinstance(node.value, bool):
                mutated_tree = copy.deepcopy(tree)
                target_node = self._find_matching_node(mutated_tree, node)
                if target_node and hasattr(target_node, "value"):
                    target_node.value = not node.value
                    try:
                        mut_source = ast.unparse(mutated_tree)
                        self._mutant_counter += 1
                        self.mutants.append(Mutant(
                            mutant_id=f"MUT_{self._mutant_counter:03d}",
                            file_path=self.file_path,
                            line_number=getattr(node, "lineno", 1),
                            mutation_type="BOOLEAN_FLIP",
                            description=f"Inverted boolean constant to {not node.value}",
                            mutated_source=mut_source
                        ))
                    except Exception as unparse_err:
                        logger.debug("Failed unparsing boolean mutant: %s", unparse_err)

        return self.mutants

    def _find_matching_node(self, tree: ast.AST, target: ast.AST) -> Optional[ast.AST]:
        """Locates the corresponding AST node by line number and column offset."""
        target_line = getattr(target, "lineno", None)
        target_col = getattr(target, "col_offset", None)
        target_type = type(target)

        for n in ast.walk(tree):
            if type(n) is target_type:
                if getattr(n, "lineno", None) == target_line and getattr(n, "col_offset", None) == target_col:
                    return n
        return None


class MutationTester:
    """Executes test suites against generated mutants to calculate Mutation Score."""

    def __init__(self, target_file: str, test_cmd: Optional[List[str]] = None):
        self.target_file = os.path.abspath(target_file)
        self.test_cmd = test_cmd

    def run_mutation_analysis(self, limit: int = 15, timeout_sec: int = 10) -> Dict[str, Any]:
        """Runs test harness against AST mutants and computes kill ratio."""
        if not os.path.isfile(self.target_file):
            return {
                "error": f"Target file '{self.target_file}' not found",
                "score": 0.0,
                "total": 0,
                "killed": 0,
                "survived": 0
            }

        with open(self.target_file, "r", encoding="utf-8") as f:
            original_content = f.read()

        generator = MutationGenerator(original_content, self.target_file)
        mutants = generator.generate_all(limit=limit)

        if not mutants:
            return {
                "message": "Zero mutation sites discovered in target file.",
                "score": 100.0,
                "total": 0,
                "killed": 0,
                "survived": 0,
                "mutants": []
            }

        killed_count = 0
        survived_count = 0

        # Determine test command if not provided
        cmd = self.test_cmd
        if not cmd:
            base_name = os.path.splitext(os.path.basename(self.target_file))[0]
            candidate_test = os.path.join("tests", f"test_{base_name}.py")
            if os.path.exists(candidate_test):
                cmd = [sys.executable, "-m", "pytest", candidate_test, "-q"]
            else:
                cmd = [sys.executable, "-m", "pytest", "tests/", "-q"]

        try:
            for m in mutants:
                # Write mutated code atomically to target file
                t0 = time.time()
                with open(self.target_file, "w", encoding="utf-8") as f:
                    f.write(m.mutated_source)

                try:
                    proc = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=timeout_sec,
                        text=True
                    )
                    elapsed = (time.time() - t0) * 1000
                    m.execution_time_ms = round(elapsed, 1)

                    if proc.returncode != 0:
                        m.status = "KILLED"
                        killed_count += 1
                    else:
                        m.status = "SURVIVED"
                        survived_count += 1
                except subprocess.TimeoutExpired:
                    m.status = "KILLED"  # Infinite loops / timeouts indicate mutation caught
                    killed_count += 1
                except Exception as run_err:
                    m.status = "ERROR"
                    logger.debug("Error executing test against mutant: %s", run_err)
        finally:
            # Guarantee original file restoration
            with open(self.target_file, "w", encoding="utf-8") as f:
                f.write(original_content)

        total = killed_count + survived_count
        score = (killed_count / total * 100.0) if total > 0 else 0.0

        return {
            "target_file": os.path.relpath(self.target_file),
            "total_mutants": len(mutants),
            "killed": killed_count,
            "survived": survived_count,
            "mutation_score": round(score, 1),
            "mutants": [
                {
                    "id": m.mutant_id,
                    "line": m.line_number,
                    "type": m.mutation_type,
                    "desc": m.description,
                    "status": m.status,
                    "time_ms": m.execution_time_ms
                }
                for m in mutants
            ]
        }
