---
name: differential-review
description: Performs security-focused differential review of code changes, commits, PRs, and diffs. Analyzes blast radius, checks test coverage of modified code, models attacker exploit paths, and generates a structured defect ledger.
metadata:
  source: trailofbits/skills
  domain: adversarial-security
---

# Differential Security Review (Trail of Bits Protocol)

Security-focused code review for pull requests, commits, and diffs.

## Core Principles
1. **Risk-First:** Focus on authentication, authorization, cryptography, token management, serialization, and external boundary calls.
2. **Evidence-Based:** Every finding must be backed by git history, line numbers, and concrete attack scenarios. Never speculate without tracing.
3. **Adaptive Scale:**
   - SMALL (<20 files): DEEP - Read all dependencies, full call graphs, and historical context.
   - MEDIUM (20-200 files): FOCUSED - 1-hop dependencies, priority risk files.
   - LARGE (200+ files): SURGICAL - Critical auth and data paths only.
4. **Honest:** Explicitly state coverage limits and confidence levels.

## Review Workflow
1. **Phase 0: Triage:** Categorize modified files by risk level (HIGH: auth, crypto, validation; MEDIUM: state mutations, APIs; LOW: UI, logging).
2. **Phase 1: Code Analysis:** Examine git blame and commit rationale. Identify removed checks, relaxed validations, or loose type coercions.
3. **Phase 2: Test Coverage:** Verify whether modified logic has corresponding unit/integration test assertions for both success and edge cases.
4. **Phase 3: Blast Radius:** Count all transitive callers of modified routines to quantify potential collateral breakage.
5. **Phase 4: Adversarial Attack Modeling:** Simulate malicious inputs (SQLi, SSRF, IDOR, race conditions, type confusion, prototype pollution).
6. **Phase 5: Structured Report:** Emit clear severity ratings, impacted files, line ranges, and reproduction steps.
