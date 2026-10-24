---
name: craftsman-evaluator
description: Autonomous self-inspection skill. Audits work against professional domain checklists before showing output to the user, ensuring zero babysitting.
---

# 🛡️ Craftsman Evaluator (Self-Inspection Protocol)

The core mechanism of **Zero Babysitting**: the agent rigorously self-evaluates its work prior to presentation.

## Self-Inspection Criteria:

1. **Completeness Verification:**
   - Are all requested features and edge cases implemented?
   - Are all functions fully realized with no placeholder comments?

2. **Quality Scoring (Target: >= 95/100):**
   - Score the draft across correctness, security, performance, and documentation.
   - Any score below 95 triggers immediate activation of `flaw-remediator`.

3. **The Mirror Test:**
   - *"Would Marcus Sterling, Diana Drake, or Elena Rostova be proud to sign their name to this output?"*
