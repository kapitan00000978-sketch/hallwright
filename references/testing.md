# 🧪 Testing Guild Reference
**Lead:** Quality Engineering Core (`hallwright_tester`)  
**Domain:** Unit Testing, Mutation Testing, Boundary Assertions & Regression Defense

---

## 🎯 Core Invariants
1. **100% Pass Invariant:** Test suites must execute to completion with 0 failures before any code modification is merged.
2. **Determinism:** Tests must be deterministic; zero reliance on network availability, clock skew, or unseeded random state.
3. **Behavior Over Implementation:** Test observable public behavior and contracts, not brittle private internal state.
4. **Hermetic Isolation:** Every test creates its own sandboxed state and cleans up all temporary files, databases, or mocks upon teardown.

---

## 📋 Quality & Security Checklist
- [ ] Boundary conditions (null, zero, empty string, max integer, unexpected types) tested explicitly.
- [ ] Error paths and exception handlers verified to trigger expected domain errors.
- [ ] Mutation testing checks that test assertions fail when underlying logic is intentionally altered.
- [ ] Async operations tested with proper timeouts and task completion assertions.
- [ ] Test execution completes within swift budget (< 60s total workspace test run).

---

## 🚫 Forbidden Anti-Patterns
- **Assertion-Free Tests:** Tests that execute code without asserting expected outcomes.
- **Flaky Tests:** Tests that periodically pass or fail based on timing or execution order.
- **Over-Mocking:** Mocking so extensively that the test passes while the real integration remains completely broken.
