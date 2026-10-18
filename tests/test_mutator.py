"""
Unit tests for Hallwright Autonomous Mutation Testing Engine (src/sdk/mutator.py).
Verifies AST mutation generation, comparison swapping, operator flips, and mutation execution.
"""

import os
import sys
import tempfile
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src", "sdk"))

from mutator import MutationGenerator, MutationTester


def test_mutation_generator_comparison_swapping():
    sample_code = """
def is_adult(age: int) -> bool:
    return age >= 18
"""
    gen = MutationGenerator(sample_code, "sample.py")
    mutants = gen.generate_all(limit=5)
    assert len(mutants) >= 1
    assert any(m.mutation_type == "COMPARISON_SWAP" for m in mutants)
    # Check that '>=' was swapped to '>'
    assert any("Flipped '>=' to strict '>'" in m.description for m in mutants)


def test_mutation_generator_operator_swapping():
    sample_code = """
def calculate_total(subtotal: float, tax: float) -> float:
    return subtotal + tax
"""
    gen = MutationGenerator(sample_code, "sample.py")
    mutants = gen.generate_all(limit=5)
    assert len(mutants) >= 1
    assert any(m.mutation_type == "OPERATOR_SWAP" for m in mutants)
    # Check that '+' was swapped to '-'
    assert any("Replaced addition '+' with subtraction '-'" in m.description for m in mutants)


def test_mutation_generator_boolean_flipping():
    sample_code = """
def is_feature_enabled() -> bool:
    return True
"""
    gen = MutationGenerator(sample_code, "sample.py")
    mutants = gen.generate_all(limit=5)
    assert len(mutants) >= 1
    assert any(m.mutation_type == "BOOLEAN_FLIP" for m in mutants)
    assert any("False" in m.mutated_source for m in mutants)


def test_mutation_tester_kills_mutants_and_preserves_original():
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Create target module
        target_file = os.path.join(tmpdir, "calculator.py")
        original_code = "def add(a: int, b: int) -> int:\n    return a + b\n"
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(original_code)

        # 2. Create test file that asserts add(2, 3) == 5
        test_file = os.path.join(tmpdir, "test_calc.py")
        test_code = (
            "import sys\n"
            f"sys.path.insert(0, r'{tmpdir}')\n"
            "from calculator import add\n"
            "def test_add():\n"
            "    assert add(2, 3) == 5\n"
        )
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_code)

        # 3. Run MutationTester
        tester = MutationTester(
            target_file=target_file,
            test_cmd=[sys.executable, "-m", "pytest", test_file, "-q"]
        )
        report = tester.run_mutation_analysis(limit=5)

        # 4. Verify mutant killed
        assert report["total_mutants"] >= 1
        assert report["killed"] >= 1
        assert report["mutation_score"] > 0.0

        # 5. Verify original file content is restored
        with open(target_file, "r", encoding="utf-8") as f:
            restored = f.read()
        assert restored == original_code
