---
name: systematic-debugging
description: Scientific 4-step root cause analysis methodology for debugging. Eliminates guess-and-check (patch-and-pray) habits.
---

# 🔍 Systematic Debugging (Scientific Root Cause Analysis)

Amateur AI models guess randomly and apply blind patches that break other components. Hallwright enforces a rigorous 4-step scientific debugging process.

## 4-Step Debugging Protocol:

1. **Step 1: Reproduce Deterministically:**
   - Create a minimal reproduction script or automated test that triggers the bug consistently.
   - Never attempt to fix a bug you cannot reliably reproduce.

2. **Step 2: Trace the Defect to the Exact Root Cause:**
   - Inspect stack traces, inspect memory states, and read logs.
   - Find the single logical error or flawed assumption that causes the failure.

3. **Step 3: Surgical Remediation:**
   - Implement the minimal, robust fix that addresses the root cause directly without touching unrelated code.
   - Add defensive checks to prevent recurrence.

4. **Step 4: Regression Verification:**
   - Run the reproduction test to prove the fix works.
   - Run the full project test suite to verify no regressions were introduced.
