---
name: test-driven-development
description: Strict Test-Driven Development (TDD) cycle: write a failing test first (Red), write minimal implementation to make it pass (Green), then refactor to perfection.
---

# 🧪 Strict Test-Driven Development (TDD)

In the Hallwright protocol, untested code is incomplete code. We adhere strictly to the Red-Green-Refactor discipline.

## TDD Lifecycle:

1. **🔴 Red Phase (Failing Test First):**
   - Write a unit or integration test that precisely tests the intended behavior or edge case.
   - Run the test suite and confirm the test **fails for the expected reason** (not due to syntax or import issues).

2. **🟢 Green Phase (Minimal Passing Implementation):**
   - Write the cleanest, most direct code necessary to make the failing test pass.
   - Avoid over-engineering during this step. Run the test and confirm it passes.

3. **🔵 Refactor Phase (Craftsmanship & Polish):**
   - Clean up architecture, eliminate duplication, optimize performance, and improve variable naming.
   - Re-run all tests to guarantee zero regressions.
