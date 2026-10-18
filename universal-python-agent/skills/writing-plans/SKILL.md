---
name: writing-plans
description: Converts approved specifications into actionable, sequential micro-tasks with clear verification criteria (Implementation Plan).
---

# 📋 Implementation Planning

An unorganized agent produces chaotic, buggy code. The Hallwright planning discipline transforms specifications into verifiable, bite-sized micro-tasks.

## Planning Structure:

1. **Phase Breakdown:**
   Divide the project into logical milestones (e.g., Phase 1: Core Domain, Phase 2: API & Storage, Phase 3: Validation & Tests).

2. **Atomic Micro-Tasks:**
   Each task must:
   - Touch a specific, bounded set of files.
   - Specify the exact classes, functions, or configurations to create or modify.
   - Have a deterministic **Verification Step** (command or test to prove it works).

3. **Risk Mitigation & Rollback Strategy:**
   - Identify brittle integration points.
   - Ensure backward compatibility and non-breaking migrations.
