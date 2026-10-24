---
name: flaw-remediator
description: Autonomous flaw remediation skill. Independently repairs any identified bug, security risk, or stylistic flaw in the background without user intervention.
---

# 🔧 Flaw Remediator (Autonomous Self-Correction)

When an audit uncovers a flaw, the agent does not announce the error to the user or ask for help. It fixes the defect autonomously in the background.

## Remediation Workflow:

1. **Triage Identified Flaws:**
   - Prioritize security vulnerabilities and broken edge cases first.
   - Address architectural flaws and code smells second.

2. **Surgical Background Patching:**
   - Refactor the code to eliminate the flaw.
   - Ensure zero regressions in neighboring modules.

3. **Final Verification:**
   - Re-evaluate using `craftsman-evaluator` until a 95+ score is confirmed.
