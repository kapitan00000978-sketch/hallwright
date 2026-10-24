---
name: audit-context-building
description: Understand a codebase before looking for bugs in it - what each function assumes, what it guarantees, and what it depends on elsewhere. Use when starting an audit, threat model, or architecture review on unfamiliar code, and before any vulnerability-hunting pass.
metadata:
  source: trailofbits/skills
  domain: security-architecture
---

# Audit Context Building (Trail of Bits Methodology)

Build understanding, not verdicts. This runs before anyone hunts for bugs, and feeds that work.

## When to Use
At the start of an audit, a threat model, or an architecture review, when the code is unfamiliar. Also when an earlier pass produced findings nobody could judge, because no one had mapped out how the system fits together.

## When NOT to Use
Do not name vulnerabilities, suggest fixes, write proofs-of-concept, or rate severity. Those belong to the hunting phase, which runs next and with the whole picture in hand. When the code counts on something and nothing checks it, record that plainly and move on — whether it matters is decided later.

## Core Rules: Follow the Calls
1. **Never trust function names or signatures:** Read the implementation line by line to discover real behavior.
2. **Catalog Unchecked Invariants:** If a function expects a non-null pointer, sanitized input, or authorized session, but never verifies it, record the missing check.
3. **Map State Transitions:** Identify every mutable global, shared memory buffer, or database row modified across call chains.
4. **Identify Blast Radius:** List all downstream consumers and upstream callers of modified or critical functions.
5. **Output Structured Dossier:**
   - Architecture Summary
   - Component Boundaries & Contracts
   - External Attack Surfaces & Trust Boundaries
   - Unenforced Assumptions Ledger (feeds the vulnerability hunter)
