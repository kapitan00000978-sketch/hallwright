# 🧬 Hallwright AST Mutation Testing

Hallwright includes a zero-dependency Abstract Syntax Tree (AST) mutation testing engine (`src/sdk/mutator.py`) to verify the fidelity and assertiveness of test suites.

---

## ⚡ Why Mutation Testing?

Code coverage metrics (e.g. 100% line coverage) only show which lines were executed during a test run, not whether the assertions would catch a subtle bug. 

Mutation testing actively introduces controlled faults (mutants) into your source code and checks whether your test suite fails. If a test fails, the mutant is **killed**. If all tests pass despite the mutation, the mutant **survives** (exposing a gap in assertions).

---

## 🔬 Mutation Operators

Hallwright applies three deterministic AST mutation classes:
1. **Comparison Mutation:** Swaps comparison operators (`==` ↔ `!=`, `<` ↔ `<=`, `>` ↔ `>=`).
2. **Binary Operator Mutation:** Inverts arithmetic and bitwise operations (`+` ↔ `-`, `*` ↔ `/`).
3. **Boolean Mutation:** Flips boolean literals (`True` ↔ `False`).

---

## 💻 CLI Usage

```bash
# Run mutation analysis on a source file against a test suite:
artisan mutate src/sdk/context_selector.py --test tests/test_smart_context.py

# With custom mutant threshold limit:
artisan mutate src/libraries/database.py --test tests/test_libraries.py --limit 15
```

---

## 📊 Output Metrics

- **Total Mutants Generated:** Count of syntactically valid code variations.
- **Mutants Killed:** Count of mutations caught by test failures.
- **Mutants Survived:** Uncaught mutations indicating assertion blind spots.
- **Mutation Score:** `(Killed / Total) * 100%`.
